document.addEventListener("DOMContentLoaded", () => {
    fetchEmergencyAlerts()
  })
  
  function fetchEmergencyAlerts() {
    fetch("/get_emergency_alerts")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        if (data.error) {
          throw new Error(data.error)
        }
        displayAlerts(data.alerts)
      })
      .catch((error) => {
        console.error("Error fetching emergency alerts:", error)
        displayError(error.message)
      })
  }
  
  function displayAlerts(alerts) {
    const alertContainer = document.getElementById("alertContainer")
    alertContainer.innerHTML = ""
  
    if (alerts.length === 0) {
      alertContainer.innerHTML = "<p>No current alerts in your area.</p>"
      return
    }
  
    alerts.forEach((alert) => {
      const alertElement = document.createElement("div")
      alertElement.className = "alert"
      alertElement.innerHTML = `
              <h3>${alert.type}</h3>
              <p>Reported ${alert.count} times in your area</p>
              <p>Stay vigilant and take necessary precautions.</p>
          `
      alertContainer.appendChild(alertElement)
    })
  }
  
  function displayError(message) {
    const alertContainer = document.getElementById("alertContainer")
    alertContainer.innerHTML = `<p>Error: ${message}. Please try again later or contact support.</p>`
  }
  
  