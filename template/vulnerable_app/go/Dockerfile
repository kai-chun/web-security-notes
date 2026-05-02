FROM golang:1.22 AS builder

WORKDIR /src
COPY go.mod ./
COPY go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/server .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /out/server /server
EXPOSE 5000
ENTRYPOINT ["/server"]
