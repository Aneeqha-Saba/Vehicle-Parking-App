<script>
import axios from "axios";

export default {
  data() {
    return {
      token: "",
      userData: [],
    };
  },
  mounted() {
    this.loadToken();
    this.loadUsers();
  },
  methods: {
    loadToken() {
      const token = localStorage.getItem("token");
      if (token) {
        this.token = token;
      }
    },
    loadUsers() {
      axios
        .get("http://127.0.0.1:5000/api/users", {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.token}`,
          },
        })
        .then((res) => {
          console.log("Users fetched:", res.data);
          this.userData = res.data;
        })
        .catch((err) => {
          console.error("Error fetching users:", err);
        });
    },
  },
};
</script>

<template>
  <div v-if="token">
    <div id="container">
      <div id="panel" style="height: auto;">
        <div class="container">
          <h1 class="text-center">Registered Users</h1>
          <br />
          <table class="table">
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Username</th>
                <th scope="col">Email</th>
                <th scope="col">Address</th>
                <th scope="col">Pin Code</th>
                <th scope="col">Parking Lots</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in userData" :key="user.id">
                <th scope="row">{{ user.id }}</th>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.address }}</td>
                <td>{{ user.pincode }}</td>
                <td>
                  <span v-if="user.parking_lots && user.parking_lots.length">
                    {{ user.parking_lots.join(", ") }}
                  </span>
                  <span v-else>N/A</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
