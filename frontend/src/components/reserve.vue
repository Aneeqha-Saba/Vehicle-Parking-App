<template>
  <div class="container mt-4">
    <h3 class="mb-4 text-center">Reserve a Parking Spot</h3>

    <form @submit.prevent="reserve">
      <div class="mb-3">
        <label for="spot_id" class="form-label">Spot ID</label>
        <input type="text" class="form-control" id="spot_id" v-model="formData.spot_id" readonly>
      </div>

      <div class="mb-3">
        <label for="lot_id" class="form-label">Lot ID</label>
        <input type="text" class="form-control" id="lot_id" v-model="formData.lot_id" readonly>
      </div>

      <div class="mb-3">
        <label for="user_id" class="form-label">User ID</label>
        <input type="text" class="form-control" id="user_id" v-model="formData.user_id" readonly>
      </div>
      <div class="mb-3">
        <label for="price" class="form-label">Price per hour(Rs.)</label>
        <input type="text" class="form-control" id="price" v-model="formData.price" readonly>
      </div>

      <div class="mb-3">
        <label for="v_num" class="form-label">Vehicle Number</label>
        <input type="text" class="form-control" id="v_num" v-model="formData.v_num" required>
      </div>

      <div class="text-center">
        <input type="submit" class="btn btn-success" value="reserve"> |
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
        lot_id: "",
        user_id: "",
        v_num: "",
        price: ""
      },
      token: localStorage.getItem("token") || ""
    };
  },
async mounted() {
  this.formData.lot_id = this.$route.params.lot_id;

  try {
    const res = await axios.get("http://127.0.0.1:5000/api/dashboard", {
      headers: { "Authorization": `Bearer ${this.token}` }
    });

    this.formData.user_id = res.data.user_id;;

  
    const lot = res.data.parking_lot_details.find(l => l.parking_lot_id == this.formData.lot_id);
    if (lot) {
      this.formData.price = lot.price;  
      const availableSpot = lot.spots.find(s => s.status === "A");
      if (availableSpot) {
        this.formData.spot_id = availableSpot.spot_id;
      } else {
        alert("No available spots in this lot");
      }
    }

  } catch (err) {
    console.error(err);
    alert("Failed to load reservation details");
  }
},
  methods: {
    async reserve() {
      try {
        const res = await axios.post(
          "http://127.0.0.1:5000/api/reserve_spot/",
          {
            lot_id: this.formData.lot_id,
            vehicle_number: this.formData.v_num
          },
          {
            headers: {
              "Authorization": `Bearer ${this.token}`,
              "Content-Type": "application/json"
            }
          }
        );
        alert(res.data.message || "Spot reserved successfully!");
        this.$router.push("/dashboard");
      } catch (err) {
        console.error(err);
        alert(err.response?.data?.message || "Reservation failed");
      }
    },
    cancel() {
      this.$router.push("/search");
    }
  }
};
</script>

