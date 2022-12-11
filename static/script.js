const $chats = document.getElementById("chats"),
	$dots = document.getElementById("dots"),
	$input = document.getElementById("input")

let INDEX = 0

function getWaitTime(msg, mul = 500) {
	return Math.min(2000, Math.random() * msg.length * mul + mul)
}

function sendClick() {
	let msg = $input.value.trim()
	if (msg == "") return false
	$input.value = ""
	appendUI(msg, 1)
	setTimeout(function () {
		$dots.style.display = "flex"
		$dots.scrollIntoView()
		respond(msg)
	}, getWaitTime(msg, 1000))
}

function appendUI(msg, person, replyindex = -1, sticker = 0) {
	const div = Object.assign(document.createElement("div"), {
		id: `msg-id-${INDEX++}`,
		className: `msg-${person}`
	})
	if (replyindex > 0 && replyindex < INDEX - 2) {
		const replyold = document.getElementById(`msg-id-${replyindex}`)
		if (replyold) {
			const replydiv = Object.assign(document.createElement("div"), { className: `msg-reply` })
			replydiv.append(replyold.textContent)
			replydiv.onclick = function () {
				replyold.scrollIntoView({ block: "center" })
				replyold.animate([
					// keyframes
					{ transform: 'scale(1)' },
					{ transform: 'scale(1.2)' }
				], {
					// timing options
					duration: 200,
					iterations: 2
				})
			}
			div.append(replydiv)
		}
	}

	if (!sticker) {
		div.append(msg)
	} else {
		const img = Object.assign(document.createElement("img"), {
			src: `/static/stickers/${msg}.webp`,
			className: `sticker`
		})
		div.appendChild(img)
		div.classList.add("sticker")
	}
	setTimeout(e => {
		$chats.insertBefore(div, $dots)
		if (person == 0) $dots.style.display = "none"
		div.scrollIntoView()
	}, person == 0 ? getWaitTime(msg) : 0)
}

function respond(msg) {
	fetch("/chat",
		{
			method: "POST",
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ prompt: msg, player: document.getElementById("player").value }),
		}).then(res => res.json()).then(data => {
			appendUI(data.reply, 0)
			if (data.sticker)
				appendUI(data.sticker, 0, -1, 1)
		})
}

function setPlayer(read = false) {
	fetch("/player",
		{
			method: "POST",
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ player: read ? -1 : document.getElementById("player").value }),
		}).then(res => res.json()).then(data => {
			console.log(data)
			if (read)
				document.getElementById("player").value = data["player"]
		})
}

function getTimeOfDay() {
	let hour = new Date().getHours()
	if (hour < 12) return "morning"
	if (hour < 18) return "afternoon"
	return "evening"
}




setPlayer(true)
appendUI(new Date().toLocaleString(), "info")
respond(`good ${getTimeOfDay()}`)