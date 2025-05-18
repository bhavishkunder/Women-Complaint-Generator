document.addEventListener("DOMContentLoaded", () => {
    fetchComplaints()
    // Add smooth scroll animation
    document.documentElement.style.scrollBehavior = "smooth"
  })
  
  async function fetchComplaints() {
    try {
      const response = await fetch("/get_user_complaints")
      const data = await response.json()
  
      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch complaints")
      }
  
      displayComplaints(data.complaints)
      // Add fade-in animation to complaints after loading
      setTimeout(() => {
        document.querySelectorAll(".complaint-card").forEach((card) => {
          card.style.opacity = "1"
          card.style.transform = "translateY(0)"
        })
      }, 100)
    } catch (error) {
      console.error("Error:", error)
      document.getElementById("complaints-container").innerHTML =
        '<div class="error-message">Failed to load complaints</div>'
    }
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }
  
  function toggleComplaintDetails(complaintId) {
    const detailsElement = document.getElementById(`complaint-details-${complaintId}`)
    const buttonText = document.getElementById(`read-btn-${complaintId}`)
    const isHidden = detailsElement.classList.contains("hidden")
  
    // Smooth transition for details
    if (isHidden) {
      detailsElement.classList.remove("hidden")
      detailsElement.style.maxHeight = "0"
      setTimeout(() => {
        detailsElement.style.maxHeight = detailsElement.scrollHeight + "px"
      }, 10)
      buttonText.textContent = "Hide Complaint"
    } else {
      detailsElement.style.maxHeight = "0"
      setTimeout(() => {
        detailsElement.classList.add("hidden")
      }, 300)
      buttonText.textContent = "Read Complaint"
    }
  }
  
  function getStatusBadgeClass(status) {
    const statusClasses = {
      submitted: "bg-blue-500",
      acknowledged: "bg-yellow-500",
      under_investigation: "bg-purple-500",
      resolved: "bg-green-500",
      forwarded: "bg-teal-500",
      rejected: "bg-red-500",
    }
    return statusClasses[status] || "bg-gray-500"
  }
  
  function displayComplaints(complaints) {
    const container = document.getElementById("complaints-container")
  
    if (!complaints || !complaints.length) {
      container.innerHTML = '<div class="text-gray-500 text-center p-4">No complaints found</div>'
      return
    }
  
    container.innerHTML = complaints
      .map(
        (complaint, index) => `
          <div class="complaint-card" style="opacity: 0; transform: translateY(20px); transition: all 0.3s ease; transition-delay: ${index * 0.1}s">
              <div class="complaint-header">
                  <div class="complaint-title">
                      <h3>Complaint #${complaint.complaint_id}</h3>
                      <span class="status-badge ${getStatusBadgeClass(complaint.status)}">
                          ${complaint.status.replace("_", " ").toUpperCase()}
                      </span>
                  </div>
                  
                  <div class="station-info ${complaint.station_name === "Not Assigned" ? "not-assigned" : "assigned"}">
                      <div class="station-header">
                          <svg xmlns="http://www.w3.org/2000/svg" class="station-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                          </svg>
                          <span class="station-name">${complaint.station_name}</span>
                      </div>
                      ${
                        complaint.station_jurisdiction
                          ? `
                          <div class="station-details">
                              <span class="jurisdiction">Jurisdiction: ${complaint.station_jurisdiction}</span>
                              ${complaint.station_contact ? `<span class="contact">Contact: ${complaint.station_contact}</span>` : ""}
                          </div>
                      `
                          : ""
                      }
                  </div>
              </div>
  
              <div class="complaint-info">
                  <div class="info-item">
                      <strong>Type:</strong> 
                      <span>${complaint.complaint_type || "Not specified"}</span>
                  </div>
                  <div class="info-item">
                      <strong>Filed:</strong> 
                      <span>${formatDate(complaint.date_created)}</span>
                  </div>
              </div>
  
              ${
                complaint.status_history && complaint.status_history.length > 1
                  ? `
                  <div class="status-timeline">
                      <h4>Status Timeline</h4>
                      <div class="timeline">
                          ${complaint.status_history
                            .map(
                              (history, index) => `
                              <div class="timeline-item">
                                  <div class="timeline-marker ${getStatusBadgeClass(history.status)}"></div>
                                  <div class="timeline-content">
                                      <div class="timeline-date">${formatDate(history.date)}</div>
                                      <div class="timeline-status">${history.status.replace("_", " ").toUpperCase()}</div>
                                      ${history.notes ? `<div class="timeline-notes">${history.notes}</div>` : ""}
                                  </div>
                              </div>
                          `,
                            )
                            .join("")}
                      </div>
                  </div>
              `
                  : ""
              }
  
              <div class="complaint-actions">
                  <button 
                      id="read-btn-${complaint.complaint_id}"
                      onclick="toggleComplaintDetails(${complaint.complaint_id})"
                      class="read-btn"
                  >
                      Read Complaint
                  </button>
                  
                  ${
                    complaint.status !== "under_investigation" && complaint.status !== "resolved"
                      ? `
                      <button 
                          onclick="cancelComplaint(${complaint.complaint_id})"
                          class="cancel-btn"
                      >
                          Cancel Complaint
                      </button>
                  `
                      : ""
                  }
              </div>
  
              <div id="complaint-details-${complaint.complaint_id}" class="complaint-details hidden">
                  <h4>Complaint Details</h4>
                  <p>${complaint.complaint_result}</p>
              </div>
          </div>
      `,
      )
      .join("")
  }
  
  async function cancelComplaint(complaintId) {
    if (!confirm("Are you sure you want to cancel this complaint? This action cannot be undone.")) {
      return
    }
  
    try {
      const response = await fetch("/delete_complaint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ complaint_id: complaintId }),
      })
  
      const result = await response.json()
  
      if (!response.ok) {
        throw new Error(result.error || "Failed to cancel complaint")
      }
  
      // Add fade-out animation before removing
      const complaintCard = document.querySelector(`[data-complaint-id="${complaintId}"]`)
      if (complaintCard) {
        complaintCard.style.opacity = "0"
        complaintCard.style.transform = "translateY(20px)"
        setTimeout(() => {
          fetchComplaints()
        }, 300)
      } else {
        fetchComplaints()
      }
    } catch (error) {
      console.error("Error:", error)
      alert("Failed to cancel complaint. Please try again later.")
    }
  }
  
  