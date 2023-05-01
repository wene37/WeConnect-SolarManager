// ReSharper disable UseOfImplicitGlobalInFunctionScope
if ("serviceWorker" in navigator) {

    window.addEventListener("load", () => {

        navigator.serviceWorker.register("/static/serviceWorker.js")
            .then((reg) => {

                var mainApp = $("#mainApp")[0];
                var applicationServerKey = mainApp.getAttribute("data-applicationServerKey");
                var applicationId = mainApp.getAttribute("data-application-id");

                if (applicationServerKey === "") {
                    //return;
                }

                if (Notification.permission === "granted") {

                    getSubscription(reg, applicationServerKey, applicationId);
                }
                else if (Notification.permission === "blocked" || Notification.permission === "denied") {
                    // do nothing
                }
                else {

                    $("#GiveAccess").show();
                    $("#PromptForAccessBtn").click(() => requestNotificationAccess(reg, applicationServerKey, applicationId));
                }
            });
    });
}

function requestNotificationAccess(reg, applicationServerKey, applicationId) {

    Notification.requestPermission(function (status) {

        $("#GiveAccess").hide();

        if (status === "granted") {
            getSubscription(reg, applicationServerKey, applicationId);
        }
    });
}

function getSubscription(reg, applicationServerKey, applicationId) {

    reg.pushManager.getSubscription().then(function (sub) {

        if (sub === null) {

            reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            }).then(function (sub) {
                sendSubscription(sub, applicationId);
            }).catch(function (e) {
                console.error("Unable to subscribe to push.", e);
            });
        } else {
            sendSubscription(sub, applicationId);
        }
    });
}

function sendSubscription(sub, applicationId) {

    const pushNotificationConfig = { endpoint: sub.endpoint, p256dh: arrayBufferToBase64(sub.getKey("p256dh")), auth: arrayBufferToBase64(sub.getKey("auth")) };

    axios.post(`/api/pushnotification?applicationId=${applicationId}`, pushNotificationConfig)
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