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
<form method="post">
  <label>Username: <input name="username"></label><br>
  <label>Password: <input name="password" type="password"></label><br>
  <button type="submit">Log in</button>
</form>
{{if .Message}}<p><b>{{.Message}}</b></p>{{end}}
`))

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatalf("open db: %v", err)
	}
	if _, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)`); err != nil {
		log.Fatalf("create table: %v", err)
	}
	// In real life, password should be hashed.
	if _, err := db.Exec(
		`INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)`,
		"administrator", "super_secret_password_123",
	); err != nil {
		log.Fatalf("seed user: %v", err)
	}
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
			log.Printf("DB error: %v", err)
		}
	}

	_ = loginTmpl.Execute(w, struct{ Message string }{Message: message})
}

func main() {
	initDB()
	defer db.Close()

	http.HandleFunc("/", login)
	log.Println("listening on :5000")
	log.Fatal(http.ListenAndServe(":5000", nil))
}
