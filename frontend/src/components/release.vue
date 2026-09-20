<template>
<div class="container mt-4">
    <h3 class="mb-4 text-center">Release a Parking Spot</h3>

    <form @submit.prevent="release">
      <div class="mb-3">
        <label for="spot_id" class="form-label">Spot ID</label>
        <input type="text" class="form-control" id="spot_id" v-model="formData.spot_id" readonly>
      </div>
      
      <div class="mb-3">
        <label for="v_num" class="form-label">Vehicle Number</label>
        <input type="text" class="form-control" id="v_num" v-model="formData.v_num" readonly>
      </div>

      <div class="mb-3">
        <label for="p_time" class="form-label">Parking Time:</label>
        <input type="text" class="form-control" id="p_time" v-model="formData.p_time" readonly>
      </div>

            
      <div class="mb-3">
        <label for="r_time" class="form-label">Releasing Time:</label>
        <input type="text" class="form-control" id="r_time" v-model="formData.r_time" readonly>
      </div>

      <div class="mb-3">
        <label for="cost" class="form-label">Total Cost:</label>
        <input type="text" class="form-control" id="cost" v-model="formData.cost" readonly>
      </div>

      <div class="text-center">
        <input type="submit" class="btn btn-success" value="release"> |
        <button type="button" class="btn btn-danger" @click="cancel">Cancel</button>
      </div>
    </form>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      formData: {
        spot_id: "",
        v_num: "",
        p_time: "",
        r_time: "",
        cost: ""
      },
      token: localStorage.getItem("token") || ""
    };
  },
  async mounted() {
    this.formData.spot_id = this.$route.params.spot_id;

    try {
      const res = await axios.get("http://127.0.0.1:5000/api/dashboard", {
        headers: { "Authorization": `Bearer ${this.token}` }
      });

      const reservation = res.data.your_bookings.find(
        r => r.spot_id == this.formData.spot_id
      );

      if (!reservation) {
        alert("Reservation not found!");
        this.$router.push("/dashboard");
        return;
      }

      this.formData.v_num = reservation.vehicle_number;
      this.formData.p_time = reservation.parking_timestamp;
      
      const now = new Date();

      
      this.formData.r_time = now.toISOString().slice(0, 19).replace("T", " ");

      
      const start = new Date(reservation.parking_timestamp); 
      const end = new Date(now.toISOString()); 

      
      const diffMs = end.getTime() - start.getTime();
      const hours = diffMs / 3600000;

      
      const safeHours = Math.max(0, hours);

      
      const rate = Number(reservation.lot_price) || 0.2;

      
      this.formData.cost = Number((safeHours * rate).toFixed(2));

      console.log("Start (UTC):", start.toISOString());
      console.log("End (UTC):", end.toISOString());
      console.log("Rate:", rate, "Hours:", safeHours, "Cost:", this.formData.cost);


    } catch (err) {
      console.error(err);
      alert("Failed to load reservation details");
    }
  },
  methods: {
    async release() {
      try {
        const res = await axios.post(
          `http://127.0.0.1:5000/api/release_spot/`,
          {
            spot_id: this.formData.spot_id,
            leaving_timestamp: this.formData.r_time,
            parking_cost: this.formData.cost
          },
          {
            headers: {
              "Authorization": `Bearer ${this.token}`,
              "Content-Type": "application/json"
            }
          }
        );

        alert(res.data.message || "Spot released successfully!");
        this.$router.push("/dashboard");
      } catch (err) {
        console.error(err);
        alert(err.response?.data?.message || "Release failed");
      }
    },
    cancel() {
      this.$router.push("/dashboard");
    }
  }
};
</script>