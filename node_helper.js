const NodeHelper = require("node_helper");
const { PythonShell } = require("python-shell");
const path = require("path");

module.exports = NodeHelper.create({
    start: function() {
        console.log("Starting node_helper for module: " + this.name);
    },

    socketNotificationReceived: function(notification, payload) {
        if (notification === "GET_POSTEN_DELIVERY_DAYS") {
            this.getPostenDeliveryDays(payload);
        }
    },

    getPostenDeliveryDays: function(postalCode) {
        const self = this;
        let options = {
            scriptPath: path.join(__dirname, "/"),  // Path to the directory of the Python script
            args: [postalCode]
        };

        PythonShell.run("posten_api_client.py", options, function(err, results) {
            if (err) {
                console.error("Error running Python script:", err);
                self.sendSocketNotification("POSTEN_DELIVERY_DAYS_ERROR", { error: err.toString() });
                return;
            }
            if (!results || results.length === 0) {
                console.error("No results received from Python script");
                self.sendSocketNotification("POSTEN_DELIVERY_DAYS_ERROR", { error: "No data received" });
                return;
            }
            try {
                console.log("Results:", results);
                let deliveryDays = JSON.parse(results.join(''));
                self.sendSocketNotification("POSTEN_DELIVERY_DAYS", deliveryDays);
            } catch (error) {
                console.error("Error parsing JSON:", error);
                self.sendSocketNotification("POSTEN_DELIVERY_DAYS_ERROR", { error: error.toString() });
            }
        });
    }
});
