<script>
import axios from "axios";

export default {
  data() {
    return {
      email: "",
      password: "",
      name: "",
      address: "",
      pincode: "",
      message: "",
    };
  },
  methods: {
    async registerUser(event) {
      event.preventDefault();

      try {
        const response = await axios.post("http://127.0.0.1:5000/api/register", {
          username: this.name,
          email: this.email,
          address: this.address,
          pincode: this.pincode,
          password: this.password,
        });

        console.log("Registration successful:", response.data);
        this.message = response.data.message;

        this.$router.push("/login");

      } catch (error) {
        console.error("Registration failed:", error.response?.data || error.message);
        this.message = error.response?.data?.message || "Registration failed.";
      }
    },
  },
};
</script>

<template>
  <div class="container" id="input-form">
    <h2 class="my-3">Register</h2>
    <form @submit="registerUser">
      <div class="mb-3">
        <label for="email">Email ID :</label>
        <input type="email" id="email" v-model="email" required />
      </div>

      <div class="mb-3">
        <label for="password">Password :</label>
        <input type="password" id="password" v-model="password" required />
      </div>

      <div class="mb-3">
        <label for="name">Username :</label>
        <input type="text" id="name" v-model="name" required />
      </div>

      <div class="mb-3">
        <label for="address">Address :</label>
        <input type="text" id="address" v-model="address" required />
      </div>

      <div class="mb-3">
        <label for="pincode">Pin Code :</label>
        <input type="text" id="pincode" v-model="pincode" required />
      </div>

      <button class="btn btn-primary" type="submit">Register</button>

      <p class="mt-3 text-success">{{ message }}</p>

      <div class="mt-3">
        <a href="/login">Already have an account? Login here</a>
      </div>
    </form>
  </div>
</template>

<style scoped>
#input-form {
  border: 1px solid blue;
  width: 600px;
  height: auto;
  margin: auto;
  margin-top: 50px;
  border-radius: 20px;
  padding: 20px;
}
</style>
