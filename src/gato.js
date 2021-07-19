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

const IKARO_ENDPOINT = PROD ? `wss://ikaro.tucanorobotics.co` : `ws://localhost:8000`
const WS_IKARO = `${IKARO_ENDPOINT}/mavlink/plate/${PLATE}`

const ws_tukano_options = {
    port: 8080,
    clientTracking: true,
}

let ws_ikaro
let ws_tukano

function aiuda() {
    console.log(">>> Executing aiuda protocol...")
    ws_tukano.close()
    ws_ikaro.terminate()
}

function tukano_connection(ws) {
    ws.on('message', function (message) {
        if (ws_ikaro.readyState === WebSocket.OPEN) {
            ws_ikaro.send(message)
            if (message.includes("HEARTBEAT")) console.log("Message TO ikaro", message)
        }
    })
    console.log("tukano service connected")
    ws_ikaro.on('message', function (message) {
        ws.send(message)
        console.log("Message FROM ikaro", message)
        clearTimeout(ws_ikaro.watchdog)
        ws_ikaro.watchdog = setTimeout(aiuda, 3000)
    })
    ws.on('error', function (e) {
        console.log("WS WS ERROR:", e)
    })
    ws.on('close', function (e) {
        console.log("WS WS CLOSE:", e)
    })
}

function connect_ikaro() {
    console.log(`Attempting connection to: ${WS_IKARO}`)
    ws_ikaro = new WebSocket(WS_IKARO)

    ws_ikaro.on('open', function (e) {
        console.log('IKARO ws connected')

        if (ws_ikaro.watchdog) clearTimeout(ws_ikaro.watchdog)
        ws_ikaro.watchdog = setTimeout(aiuda, 3000)

        try {
            ws_tukano = new WebSocket.Server(ws_tukano_options)
        } catch {
            ws_tukano.close()
            ws_tukano = new WebSocket.Server(ws_tukano_options)
        }
        ws_tukano.on('error', function (e) {
            console.log("WS TUKANO ERROR:", e)
        })
        ws_tukano.on('close', function (e) {
            console.log("WS TUKANO CLOSE:", e)
        })
        ws_tukano.on('connection', tukano_connection)
    })
    ws_ikaro.on('close', function (e) {
        console.log('IKARO ws is closed. Reconnecting in 1 second:', e)
        if (ws_tukano) ws_tukano.close()
        setTimeout(function () { connect_ikaro() }, 1000)
    })
    ws_ikaro.on('error', function (e) {
        console.log('IKARO ws error: ', e.name + ': ' + e.message)
        ws_ikaro.terminate()
    })
}

connect_ikaro()
