const WebSocket = require('ws')

const PLATE = process.env.PLATE || "00000000"

const TUKANO_ENV = process.env.TUKANO_ENV || "DEV"
const PROD = TUKANO_ENV === "PROD"

const IKARO_ENDPOINT = PROD ? `wss://icaro.tucanorobotics.co` : `ws://localhost:8000`
const WS_IKARO = `${IKARO_ENDPOINT}/mavlink/plate/${PLATE}`

const ws_ikaro = new WebSocket(WS_IKARO)
const ws_tukano = new WebSocket.Server({ port: 8080 })

ws_tukano.on('connection', function connection(ws) {
    ws.on('message', function incoming(message) {
        ws_ikaro.send(message)
    })
    ws_ikaro.on('message', function incoming(message) {
        ws.send(message)
    })
})
