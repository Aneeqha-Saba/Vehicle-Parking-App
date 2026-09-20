<script>
import axios from "axios";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(Title, Tooltip, Legend, BarElement, ArcElement, CategoryScale, LinearScale);

export default {
  components: { Bar},
  data() {
    return {
      token: "",
      role: "",
      adminData: [],
      userData: {},
    };
  },
  async mounted() {
    this.token = localStorage.getItem("token") || "";
    await this.loadSummary();
  },
  methods: {
    async loadSummary() {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/dashboard", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.role = res.data.role;

        const summaryRes = await axios.get("http://127.0.0.1:5000/api/summary", {
          headers: { Authorization: `Bearer ${this.token}` },
        });

        if (this.role === "admin") {
          this.adminData = summaryRes.data;
        } else {
          this.userData = summaryRes.data;
        }
      } catch (err) {
        console.error("Error loading summary:", err);
      }
    },
  },
  computed: {
    adminChartData() {
      return {
        labels: this.adminData.map((lot) => lot.lot_name),
        datasets: [
          {
            label: "Available Spots",
            data: this.adminData.map((lot) => lot.available),
            backgroundColor: "rgba(0, 0, 255)",
          },
          {
            label: "Occupied Spots",
            data: this.adminData.map((lot) => lot.occupied),
            backgroundColor: "rgba(255, 0, 0)",
          },
        ],
      };
    },
    userChartData() {
      return {
        labels: Object.keys(this.userData),
        datasets: [
          {
            label: "Times Parked",
            data: Object.values(this.userData),
            backgroundColor: "rgba(0, 0, 255)",
          },
        ],
      };
    },
  },
};
</script>

<template>
  <div class="summary-container">
    <h2 class="text-center">Summary</h2>

    <div v-if="role === 'admin'">
      <h4>Available vs Occupied Spots</h4>
      <Bar :data="adminChartData" />

    </div>

    <div v-else>
      <h4>Your Parking Usage Summary</h4>
      <Bar :data="userChartData" />
    </div>
  </div>
</template>

<style scoped>
.summary-container {
  max-width: 700px;
  margin: 30px auto;
  text-align: center;
}
h2 {
  margin-bottom: 20px;
}
h4 {
  margin: 25px 0 15px;
}
</style>
