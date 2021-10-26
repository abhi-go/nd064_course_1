FROM golang:alpine
WORKDIR /go/src/app
ADD . .
RUN go build -o helloworld main.go
EXPOSE 6111
CMD ["./helloworld"]
