// ReSharper disable UseOfImplicitGlobalInFunctionScope
// ReSharper disable Html.EventNotResolved
self.addEventListener("push", function (e) {

    if (!e.data) {

        console.log("No payload");
        return;
    }

    const payload = JSON.parse(e.data.text());
    const options = {
        body: payload.message,
        tag: payload.tag,
        icon: "/images/favicon/icon-512.png",
        vibrate: [100, 50, 100],
        timestamp: Date.parse(payload.dateTime)/*,
        actions: [
            {
                action: "explore", title: "Go interact with this!",
                icon: "images/checkmark.png"
            },
            {
                action: "close", title: "Ignore",
                icon: "images/red_x.png"
            }
        ]*/
    };

    e.waitUntil(
        self.registration.showNotification("SensorHome - " + payload.title, options)
    );
});

self.addEventListener("notificationclick", function (e) {

    const notification = e.notification;
    const action = e.action;

    if (action === "close") {
        notification.close();
    } else {
        // Some actions
        clients.openWindow("https://sensorhome.witro.ch");
        notification.close();
    }
});