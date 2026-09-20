<template>
  <div>
    <div v-if="role">
      <div class="container mt-4">
        <div class="card body text-center mb-3">
          <h3 v-if="role === 'user'">Search Parking Lots</h3>
          <h3 v-else>Search Users</h3>
        </div>
        <div class="row mb-3">
          <div class="col-md-6">
            <input
              v-model="searchText"
              @keyup.enter="onSearch"
              class="form-control"
              :placeholder="role === 'admin' ? 'Enter User ID' : 'Enter Prime Location Name'"
            />
          </div>

          <div class="col-md-3">
            <button class="btn btn-primary" @click="onSearch">Search</button>
            <button class="btn btn-secondary ms-2" @click="clearSearch">Clear</button>
          </div>
        </div>
        <div v-if="role === 'user'">
          <table class="table table-bordered" v-if="searchResults.length">
            <thead>
              <tr>
                <th>ID</th>
                <th>Address</th>
                <th>Prime Location</th>
                <th>Availability</th>
                <th>Price per hour (Rs.)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lot in searchResults" :key="lot.parking_lot_id">
                <td>{{ lot.parking_lot_id }}</td>
                <td>{{ lot.address }}</td>
                <td>{{ lot.prime_location_name }}</td>
                <td>{{ lot.available_spots }} / {{ lot.total_spots }}</td>
                <td>Rs.{{ lot.price }}</td>
                <td>
                  <RouterLink :to="`/user/reserve/${lot.parking_lot_id}`">
                    <button class="btn btn-primary">Book Now</button>
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="alert alert-info">No parking lots found.</div>
        </div>
        <div v-else>
          <table class="table table-bordered" v-if="searchResults.length">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Address</th>
                <th>Pincode</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in searchResults" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.name }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.address }}</td>
                <td>{{ u.pincode }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="alert alert-info">No users found.</div>
        </div>
      </div>
    </div>

    <div v-else class="text-center mt-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { RouterLink } from "vue-router";

export default {
  components: { RouterLink },
  data() {
    return {
      token: "",
      role: "",
      userData: {},
      searchText: "",
      searchResults: [],
    };
  },
  mounted() {
    this.loadToken();
    this.loadUser();
  },
  methods: {
    loadToken() {
      const token = localStorage.getItem("token");
      if (token) this.token = token;
    },
    loadUser() {
      axios
        .get("http://127.0.0.1:5000/api/dashboard", {
          headers: { Authorization: `Bearer ${this.token}` },
        })
        .then((res) => {
          this.role = res.data.role;
          this.userData = res.data;
        })
        .catch((err) => console.error(err));
    },
    onSearch() {
      if (!this.searchText.trim()) {
        alert("Please enter search text.");
        return;
      }

      axios
        .post(
          "http://127.0.0.1:5000/api/search",
          { text_search: this.searchText.trim() },
          { headers: { Authorization: `Bearer ${this.token}` } }
        )
        .then((res) => {
          this.searchResults = res.data.search_results || [];
        })
        .catch((err) => {
          const msg = err?.response?.data?.message || "Search failed";
          alert(msg);
        });
    },
    clearSearch() {
      this.searchText = "";
      this.searchResults = [];
    },
  },
};
</script>