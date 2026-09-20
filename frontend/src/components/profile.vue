<template>
  <div class="container mt-4">
    <h3 class="text-center mb-4">Edit Profile</h3>

    <form @submit.prevent="updateProfile" class="card p-4 shadow-sm">
      <div class="mb-3">
        <label class="form-label">Name</label>
        <input v-model="profileData.name" type="text" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="profileData.password" type="password" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="profileData.email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Address</label>
        <input v-model="profileData.address" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Pincode</label>
        <input v-model="profileData.pincode" type="text" class="form-control" required />
      </div>
      <div class="text-center">
          <button type="submit" class="btn btn-success">Update</button> | 
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
      token: "",
      role: "",
      profileData: { name: "",password: "", email: "", address: "", pincode: "" },
    };
  },
  mounted() {
    this.token = localStorage.getItem("token");
    this.loadProfile();
  },
  methods: {
    loadProfile() {
      axios
        .get("http://127.0.0.1:5000/api/dashboard", {
          headers: { Authorization: `Bearer ${this.token}` },
        })
        .then((res) => {
          this.role = res.data.role;
          if (this.role === "admin") {
            this.profileData.name = res.data.admin_name;
          } else {
            this.profileData.name = res.data.user_name;
          }
          this.profileData.password = res.data.password || "";
          this.profileData.email = res.data.email;
          this.profileData.address = res.data.address;
          this.profileData.pincode = res.data.pincode;
        });
    },
    updateProfile() {
      axios.post(
          "http://127.0.0.1:5000/api/update_profile",
          this.profileData,
          { headers: { Authorization: `Bearer ${this.token}` } }
        )
        .then(() => {
            alert("Profile updated successfully!");
            this.$router.push("/dashboard");
        })
        .catch(() => alert("Failed to update profile"));
    },
  },
};
</script>
