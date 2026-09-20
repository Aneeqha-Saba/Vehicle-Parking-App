<template>
  <div v-if="token">
    <div v-if="role == 'user'">    
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <RouterLink class="navbar bg-primary-subtle px-3 py-2 rounded" to="/dashboard">
              Vehicle Parking App
            </RouterLink>
          </h5>
          <label class="mb-0 text-center">Welcome {{ userData.user_name }}!!</label>
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/search">Bookings</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/summary">Summary</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/profile">Profile</RouterLink>
            </li>
            <li class="nav-item">
              <button class="btn btn-link text-danger" @click="logoutUser">Logout</button>
            </li>
          </ul>
        </div>
      </nav>
    </div>
    <div v-if="role == 'admin'">
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <RouterLink class="navbar bg-primary-subtle px-3 py-2 rounded" to="/dashboard">
              Vehicle Parking App
            </RouterLink>
          </h5>
          <h5 class="mb-0 text-center">Welcome {{ userData.admin_name }}!!</h5>
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/user">Users</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/search">Search</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/summary">Summary</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="btn btn-link" to="/profile">Profile</RouterLink>
            </li>
            <li class="nav-item">
              <button class="btn btn-link text-danger" @click="logoutUser">Logout</button>
            </li>
          </ul>
        </div>
      </nav>
    </div>
  </div>
  <div v-else>
    <nav class="navbar bg-primary-subtle">
      <div class="container-fluid">   
        <RouterLink class="navbar-brand" to="/">Vehicle Parking App</RouterLink>
      </div>
    </nav>
  </div>
</template>



<script>
import axios from 'axios';

export default {
  data() {
    return {
      token: "",
      role: "",
      userData: "",
      showProfileModal: false
    };
  },
  mounted() {
    this.refreshUserData();
  },
  watch: {
    $route() {
      this.refreshUserData();
    }
  },
  methods: {
    refreshUserData() {
      const token = localStorage.getItem("token");
      this.token = token ? token : "";

      if (this.token) {
        axios.get("http://127.0.0.1:5000/api/dashboard", {
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.token}`
          }
        })
        .then(res => {
          this.role = res.data.role;
          this.userData = res.data;
        })
        .catch(() => {
          this.token = "";
          this.role = "";
          this.userData = "";
        });
      } else {
        this.role = "";
        this.userData = "";
      }
    },
    logoutUser() {
      localStorage.clear();
      this.token = "";
      this.role = "";
      this.userData = "";
      this.$router.push('/');
    }
  }
};
</script>
