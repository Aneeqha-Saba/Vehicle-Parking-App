<style>
.space{
    padding: 10px;
}
</style>
<template>
<!-- User Dashboard-->    
    <div v-if="token">
        <div id="container">
        <div id="panel" style="height: auto;">
        <div v-if="role == 'user'">
                    <!-- Recent Parking History -->
            <div class="container mt-4">
                <h3 class="text-center">Recent Parking History</h3>
                <br>
                <table class="table table-bordered">
                            <thead>
                        <tr>
                            <th scope="col" style="width: 5%;">Reservation ID</th>
                            <th scope="col" style="width: 5%;">Parking Lot ID</th>
                            <th scope="col" style="width: 5%;">Parking Spot ID</th>
                            <th scope="col" style="width: 10%;">Location Name</th>
                            <th scope="col" style="width: 10%;">Vehicle Number</th>
                            <th scope="col" style="width: 20%;">Start Time</th>
                            <th scope="col" style="width: 20%;">End Time</th>
                            <th scope="col" style="width: 10%;">Cost</th>
                            <th scope="col" style="width: 20%;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="bookings in userData.your_bookings" :key="bookings.reservation_id">
                             <td>{{ bookings.reservation_id }}</td>
                            <td>{{ bookings.lot_id }}</td>
                            <td>{{ bookings.spot_id }}</td>
                            <td>{{ bookings.location_name }}</td>
                            <td>{{ bookings.vehicle_number }}</td>
                            <td>{{ bookings.parking_timestamp }}</td>
                            <td>{{ bookings.leaving_timestamp }}</td>
                            <td>{{ bookings.Cost }}</td>
                            <td>
                                <div v-if="bookings.status === 'Occupied'">
                                    <RouterLink :to="`/user/release/${bookings.spot_id}`">
                                        <button type="button" class="btn btn-danger">Release</button>
                                    </RouterLink>
                                </div>
                                <div v-else>
                                    <button type="button" class="btn btn-success" disabled>Released</button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Admin Dashboard-->
        <div v-if="role == 'admin'">
            <!-- Main Content
            style="height: 500px; -->
            <div class="container mt-4">
                <h1 class="text-center mb-4">Parking Lot</h1>
                <div class="text-center mb-3">
                  <button class="btn btn-primary" @click="downloadCSV">
                    Download Report
                  </button>
                </div>
                <!-- Parking Lot Card -->
            <div class="d-flex flex-wrap justify-content-center">
                <div class="card mx-auto" style="width: 20rem;" v-for="lots in userData.parking_lot_details" :key="lots.parking_lot_id">
                    <div class="card-body">
                        <h5 class="card-title">{{ lots.prime_location_name }}</h5>
                        <p>
                            <RouterLink class="btn btn-link" :to="`/admin/edit_lot/${lots.parking_lot_id}`" >
                                Edit
                            </RouterLink> |
                            <RouterLink class="text-danger ms-2" :to="`/admin/delete_lot/${lots.parking_lot_id}`">
                                Delete
                            </RouterLink>
                        </p>
                        <p>Occupied spots: {{ lots.occupied_spots }}/{{ lots.total_spots }}</p>
                    </div>

                    <div class="card-footer">
                        <h6 class="mb-2">Parking Spots</h6>
                    </div>
                    <div class="btn-toolbar space" role="toolbar">
                        <div v-for="spot in lots.spots" :key="spot.spot_id" class="btn-group me-2 mb-2" role="group">
                            <button type="button" class="btn" data-bs-toggle="modal" data-bs-target="#exampleModal" :class="spot.status === 'Available' ? 'btn-success' : 'btn-danger'" @click="openSpotModal(spot)"> 
                                {{  spot.status === 'Available' ? 'A' : 'O' }}                                    
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <br></br>
                <!-- View/Delete Parking Spot Modal -->
                <div class="modal fade" id="spotModal" tabindex="-1" aria-labelledby="spotModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                    <div class="modal-header bg-warning-subtle">
                        <h5 class="modal-title fw-bold">View/Delete Parking Spot</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>

                    <div class="modal-body">
                        <p><strong>ID:</strong> {{ selectedSpot.spot_id }}</p>
                        <p>
                        <strong>Status:</strong>
                        <span
                            v-if="selectedSpot.status === 'Available'"
                            class="badge bg-success"
                        >
                            A
                        </span>
                        <button v-else type="button" class="btn btn-sm btn-danger" id="popoverButton">
                            O
                        </button>
                        </p>

                        <p class="text-danger fst-italic small">
                        Note: Can't delete the occupied parking spot
                        </p>
                    </div>

                    <div class="modal-footer">
                        <button v-if="selectedSpot.status === 'Available'" type="button" Class="btn btn-danger" @click="deleteSpot(selectedSpot.spot_id)">
                        Delete
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        Close
                        </button>
                    </div>
                    </div>
                </div>
                </div>


            <div class="mb-4" style="text-align: center;">
                <RouterLink to="/admin/create_lot">
                    <button class="btn btn-primary"> Add Parking Lot </button>
                </RouterLink>
            </div>
            <br></br>
        </div>
        </div>
        </div>
        </div>
    </div>
    <div v-else>
        please login to access dashboard
    </div>
</template>


<script>
import axios from "axios";
import * as bootstrap from "bootstrap";

export default {
  data() {
    return {
        token: "",
        role: "",
        userData: "",
        selectedSpot: {},
        popoverInstance: null,
    };
  },
  mounted() {
    this.loadtoken();
    this.loadUser();
  },
  methods: {
    loadtoken() {
      const token = localStorage.getItem("token");
      if (token) {
        this.token = token;
      }
    },
    loadUser() {
      axios
        .get("http://127.0.0.1:5000/api/dashboard", {
          headers: {"Content-Type": "application/json",
            Authorization: `Bearer ${this.token}`,
          },
        })
        .then((res) => {
          console.log(res);
          this.role = res.data.role;
          this.userData = res.data;
        })
        .catch((err) => (this.error = err.response.data.message));
    },
    openSpotModal(spot) {
      this.selectedSpot = { ...spot };

      const lot = this.userData.parking_lot_details.find(l =>l.spots.some(s => s.spot_id === spot.spot_id));

      if (!spot.parking_cost && spot.parking_timestamp && spot.status === "Occupied") {
        const parkingTime = new Date(spot.parking_timestamp);
        const now = new Date();
        const diffHours = (now - parkingTime) / (1000 * 60 * 60);
        const ratePerHour = lot.price || 0;
        this.selectedSpot.parking_cost = Math.round(diffHours * ratePerHour);
      }

      this.$nextTick(() => {
        const popoverBtn = document.getElementById("popoverButton");

        if (popoverBtn && this.selectedSpot.status === "Occupied") {
          if (this.popoverInstance) {
            this.popoverInstance.dispose();
          }

          this.popoverInstance = new bootstrap.Popover(popoverBtn, {
            html: true,
            trigger: "click",
            placement: "right",
            content: `
              <b>ID:</b> ${spot.spot_id}<br>
              <b>Customer ID:</b> ${spot.occupied_by_id || "N/A"}<br>
              <b>Vehicle:</b> ${spot.vehicle_number || "N/A"}<br>
              <b>Booking Time:</b> ${spot.parking_timestamp || "N/A"}<br>
              <b>Price:</b> Rs. ${this.selectedSpot.parking_cost || "N/A"}
            `,
          });
        }
      });

      const modalEl = document.getElementById("spotModal");
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    },
    deleteSpot(spot_id) {
      if (!confirm("Are you sure you want to delete this parking spot?")) return;

      axios
        .delete(`http://127.0.0.1:5000/api/parking_spot/${spot_id}`, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.token}`,
          },
        })
        .then((res) => {
          alert(res.data.message || "Parking spot deleted successfully!");
          
          const modalEl = document.getElementById("spotModal");
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();

          this.loadUser();
        })
        .catch((err) => {
          console.error(err);
          alert(err.response?.data?.message || "Failed to delete parking spot.");
        });
    },
    async downloadCSV() {
    try {
      const start = await axios.get("http://127.0.0.1:5000/export_csv");
      const taskId = start.data.id;
      const check = setInterval(async () => {
        try {
          const res = await axios.get(
            `http://127.0.0.1:5000/api/csv_result/${taskId}`,
            { responseType: "blob",
              validateStatus: () => true,
            }
          );
          if (res.status === 202) {
            return;
          }
          clearInterval(check);
          const blob = new Blob([res.data], { type: "text/csv" });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.click();
        } catch (err) {
        }
      }, 2000);
    } catch (err) {
      alert("Failed to generate CSV");
      console.error(err);
    }
    },
  },
};
</script>