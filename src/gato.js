require('dotenv').config({ path: './env/defaults.env' })

const original_log = console.log
console.log = function(...arguments) {
    const ts = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
    original_log.apply(console, [`[${ts}]`, ...arguments])
}

if (process.env.GATO_ENABLED !== 'true') return console.log("gato proxy not enabled")

const WebSocket = require('ws')

const PLATE = process.env.PLATE || "00000000"

const TUKANO_ENV = process.env.TUKANO_ENV || "DEV"
const PROD = TUKANO_ENV === "PROD"

const IKARO_ENDPOINT = PROD ? `wss://icaro.tucanorobotics.co` : `ws://localhost:8000`
const WS_IKARO = `${IKARO_ENDPOINT}/mavlink/plate/${PLATE}`

let ws_ikaro
const ws_tukano = new WebSocket.Server({ port: 8080 })

function tukano_connection (ws) {
    ws.on('message', function (message) {
        if (ws_ikaro.readyState === WebSocket.OPEN) {
            ws_ikaro.send(message)
            console.log("Message TO ikaro", message)
        }
    })
    console.log("tukano service connected")
    ws_ikaro.on('message', function (message) {
        ws.send(message)
        console.log("Message FROM ikaro", message)
    })
    ws.on('error', function (e) {
        console.log("WS WS ERROR:", e)
    })
    ws.on('close', function (e) {
        console.log("WS WS CLOSE:", e)
    })
}

ws_tukano.on('error', function (e) {
    console.log("WS TUKANO ERROR:", e)
})

ws_tukano.on('close', function (e) {
    console.log("WS TUKANO CLOSE:", e)
})

function connect_ikaro() {
    ws_ikaro = new WebSocket(WS_IKARO)

    ws_ikaro.on('open', function (e) {
        console.log('IKARO ws connected')
        ws_tukano.on('connection', tukano_connection)
    })
    ws_ikaro.on('close', function (e) {
        console.log('IKARO ws is closed. Reconnecting in 1 second:', e)
        setTimeout(function () { connect_ikaro() }, 1000)
    })
    ws_ikaro.on('error', function (e) {
        console.log('IKARO ws error: ', e.name + ': ' + e.message)
        ws_ikaro.terminate()
    })
}

connect_ikaro()
