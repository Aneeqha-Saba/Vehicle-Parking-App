<template>
<div class="container mt-4">
    <h3 class="mb-4 text-center">Editing a Parking Lot</h3>

    <form @submit.prevent="edit_lot">
      <div class="mb-3">
        <label for="prime_location_name" class="form-label">Prime Location Name:</label>
        <input type="text" class="form-control" id="prime_location_name" v-model="formData.prime_location_name" required>
      </div>
      
      <div class="mb-3">
        <label for="address" class="form-label">Address</label>
        <input type="text" class="form-control" id="address" v-model="formData.address" required>
      </div>

      <div class="mb-3">
        <label for="pin_code" class="form-label">Pin Code</label>
        <input type="text" class="form-control" id="pin_code" v-model="formData.pin_code" required>
      </div>
            
      <div class="mb-3">
        <label for="price" class="form-label">Price per hour:</label>
        <input type="text" class="form-control" id="price" v-model="formData.price" required>
      </div>

      <div class="mb-3">
        <label for="number_of_spots" class="form-label">Maximum Spots:</label>
        <input type="text" class="form-control" id="number_of_spots" v-model="formData.number_of_spots" required>
      </div>

      <div class="text-center">
        <input type="submit" class="btn btn-success" value="Update"> |
        <button type="button" class="btn btn-danger" @click="cancel">Cancel</button>
      </div>
    </form>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  data() {
    return {
      formData: {
        prime_location_name: '',
        price: '',
        address: '',
        pin_code: '',
        number_of_spots: ''
      },
      lot_id: null
    };
  },

  mounted() {
    this.lot_id = this.$route.params.lot_id;
    this.fetchLotData(); 
  },

  methods: {
    fetchLotData() {
      if (!localStorage.getItem("token")) {
        alert("Please login to continue");
        this.$router.push("/login");
        return;
      }

      axios.get(`http://127.0.0.1:5000/api/edit_lot/${this.lot_id}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      })
      .then(res => {
        this.formData = res.data;
      })
      .catch(err => {
        console.error(err);
        alert("Failed to load parking lot data");
      });
    },

    edit_lot() {
      if (!localStorage.getItem("token")) {
        alert("Please login to continue");
        this.$router.push("/login");
        return;
      }

      axios.put(`http://127.0.0.1:5000/api/edit_lot/${this.lot_id}`, this.formData, {
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      })
      .then(res => {
        alert(res.data.message);
        this.$router.push("/dashboard");
      })
      .catch(err => {
        console.error(err);
        alert("Failed to update parking lot");
      });
    },

    cancel() {
      this.$router.push("/dashboard");
    }
  }
};
</script>
