if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker.register("/static/serviceWorker.js")
            .then((reg) => {

                var mainApp = $("#mainApp")[0];
                var applicationServerKey = mainApp.getAttribute("data-applicationServerKey");

                if (applicationServerKey === "") {
                    return;
                }

                if (Notification.permission === "granted") {

                    getSubscription(reg, applicationServerKey);
                }
                else if (Notification.permission === "blocked" || Notification.permission === "denied") {
                    // do nothing
                }
                else {

                    $("#GiveAccess").show();
                    $("#PromptForAccessBtn").click(() => requestNotificationAccess(reg, applicationServerKey));
                }
            });
    });
}

function requestNotificationAccess(reg, applicationServerKey) {

    Notification.requestPermission(function (status) {

        $("#GiveAccess").hide();

        if (status === "granted") {
            getSubscription(reg, applicationServerKey);
        }
    });
}

function getSubscription(reg, applicationServerKey) {

    reg.pushManager.getSubscription().then(function (sub) {

        if (sub === null) {

            reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            }).then(function (sub) {
                sendSubscription(sub);
            }).catch(function (e) {
                console.error("Unable to subscribe to push.", e);
            });
        } else {
            sendSubscription(sub);
        }
    });
}

function sendSubscription(sub) {

    const pushNotificationConfig = { endpoint: sub.endpoint, p256dh: arrayBufferToBase64(sub.getKey("p256dh")), auth: arrayBufferToBase64(sub.getKey("auth")) };

    axios.post(`/api/pushnotification`, pushNotificationConfig)
    .then(res => {
        console.log(res);
    })
    .catch(function () {
        console.log("An error occurred while saving push notification config.");
    });
}

function arrayBufferToBase64(buffer) {

    var binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;

    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }

    return window.btoa(binary);
}