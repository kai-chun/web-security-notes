// Test the vulnerability:
// curl -s http://localhost:8002 --cookie "TrackingId=TFYzlWqLrDp413AF"

package main

import (
	"database/sql"
	"errors"
	"fmt"
	"html/template"
	"log"
	"net/http"

	_ "modernc.org/sqlite"
)

const dbPath = "users.db"

var loginTmpl = template.Must(template.New("login").Parse(`
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<section>
    <a href="/">Home</a><p>|</p>
    {{ if .TracedMsg }}<div>{{ .TracedMsg }}</div><p>|</p>{{ end }}
    <a href="/my-account">My account</a><p>|</p>
</section>
<form method="post" action="login">
  <label>Username: <input name="username"></label><br>
  <label>Password: <input name="password" type="password"></label><br>
  <button type="submit">Log in</button>
</form>
{{ if .Message }}<p><b>{{ .Message }}</b></p>{{ end }}
`))

var db *sql.DB

type MsgStruct struct {
	TracedMsg string
	Message   string
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatalf("open db: %v", err)
	}
	// Insert a sample user
	if _, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)`); err != nil {
		log.Fatalf("create table: %v", err)
	}
	if _, err := db.Exec(
		`INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)`,
		"administrator", "supersecretpassword123",
	); err != nil {
		log.Fatalf("seed user: %v", err)
	}
	// Insert a sample tracking ID
	if _, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS tracked_users (
			id INTEGER PRIMARY KEY,
			tracking_id TEXT NOT NULL UNIQUE
		) `); err != nil {
		log.Fatalf("create table: %v", err)
	}
	if _, err := db.Exec(
		"INSERT OR IGNORE INTO tracked_users (tracking_id) VALUES (?)",
		"TFYzlWqLrDp413AF",
	); err != nil {
		log.Fatalf("seed tracked user: %v", err)
	}
}

func getPage(w http.ResponseWriter, r *http.Request) {
	var tracedMsg string

	cookie, cookieErr := r.Cookie("TrackingId")
	if cookieErr != nil {
		_ = loginTmpl.Execute(w, &MsgStruct{})
		return
	}
	trackingId := cookie.Value

	query := fmt.Sprintf(
		"SELECT tracking_id FROM tracked_users WHERE tracking_id = '%s'",
		trackingId,
	)

	log.Printf("[DEBUG] Executing: %s", query)

	var trackedUser string
	err := db.QueryRow(query).Scan(&trackedUser)
	switch {
	case err == nil:
		tracedMsg = "Welcome back"
	case errors.Is(err, sql.ErrNoRows):
		tracedMsg = ""
	default:
		// Leaking error messages also helps attackers — another bad practice.
		tracedMsg = ""
	}

	_ = loginTmpl.Execute(w, &MsgStruct{
		TracedMsg: tracedMsg,
		Message:   "",
	})
}

func login(w http.ResponseWriter, r *http.Request) {
	var message string

	if r.Method == http.MethodPost {
		username := r.FormValue("username")
		password := r.FormValue("password")

		query := "SELECT id, username FROM users WHERE username = ? AND password = ?"

		var id int
		var name string
		err := db.QueryRow(query, username, password).Scan(&id, &name)
		switch {
		case err == nil:
			message = fmt.Sprintf("Welcome, %s! (id=%d)", name, id)
		case errors.Is(err, sql.ErrNoRows):
			message = "Invalid credentials"
		default:
			// Leaking error messages also helps attackers — another bad practice.
			message = fmt.Sprintf("DB error: %v", err)
		}
	}

	_ = loginTmpl.Execute(w, &MsgStruct{
		TracedMsg: "",
		Message:   message,
	})

}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/", getPage)
	http.HandleFunc("/login", login)
	log.Println("listening on :5000")
	log.Fatal(http.ListenAndServe(":5000", nil))
}
