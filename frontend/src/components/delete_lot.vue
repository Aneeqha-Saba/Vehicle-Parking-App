<template>
<div class="container mt-4">
    <h3 class="mb-4 text-center">Deleting a Parking Lot</h3>

    <form @submit.prevent="delete_lot">
      <div class="mb-3">
        <label for="prime_location_name" class="form-label">Prime Location Name:</label>
        <input type="text" class="form-control" id="prime_location_name" v-model="formData.prime_location_name" readonly>
      </div>
      
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <input type="text" class="form-control" id="address" v-model="formData.address" readonly>
      </div>

      <div class="mb-3">
        <label for="pin_code" class="form-label">Pin Code</label>
        <input type="text" class="form-control" id="pin_code" v-model="formData.pin_code" readonly>
      </div>
            
      <div class="mb-3">
        <label for="price" class="form-label">Price per hour:</label>
        <input type="text" class="form-control" id="price" v-model="formData.price" readonly>
      </div>

      <div class="mb-3">
        <label for="number_of_spots" class="form-label">Maximum Spots:</label>
        <input type="text" class="form-control" id="number_of_spots" v-model="formData.number_of_spots" readonly>
      </div>

      <div class="text-center">
        <input type="submit" class="btn btn-success" value="Delete"> |
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
      lot_id: null,
      formData: {
        prime_location_name: "",
        price: "",
        address: "",
        pin_code: "",
        number_of_spots: "",
      }
    };
  },
  mounted() {
    this.lot_id = this.$route.params.lot_id; 
    this.fetchLot();
  },
  methods: {
    fetchLot() {
      axios
        .get(`http://127.0.0.1:5000/api/edit_lot/${this.lot_id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        })
        .then((res) => {
          this.formData = res.data;
        })
        .catch((err) => {
          console.error(err);
          alert("Failed to load parking lot details");
        });
    },

    delete_lot() {
      if (confirm("Are you sure you want to delete this parking lot?")) {
        axios
          .delete(`http://127.0.0.1:5000/api/delete_lot/${this.lot_id}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          })
          .then((res) => {
            alert(res.data.message);
            this.$router.push("/dashboard");
          })
          .catch((err) => {
            console.error(err);
            alert("Failed to delete parking lot");
          });
      }
    },

    cancel() {
      this.$router.push("/dashboard");
    },
  },
};
</script>
