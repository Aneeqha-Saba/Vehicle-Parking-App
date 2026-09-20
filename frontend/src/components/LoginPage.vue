<script>
import axios from 'axios'
export default {
  data(){
    return {
      formData:{
        username: '',
        password: ''
      },
      token: "",
      error: ""
    }
  },
  methods:{
    LoginUser(event){
      event.preventDefault()
      // console.log(`Username: ${this.formData.username}, Password: ${this.formData.password}`)
      const response = axios.post("http://127.0.0.1:5000/api/login", JSON.stringify(this.formData), {
       headers :  {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
      })
      response
      .then(res => {
          this.token = res.data.access_token
          localStorage.setItem("token", res.data.access_token)
          this.$router.push('/dashboard')
      }) .catch(err => this.error = err.response.data.message)
    }
  }
}

</script>


<template>
    <div id="container">
        <div id="panel" style="height: 600px;">
            <div id="input-form" style="height: 400px;">
                <h2>Login</h2>
                <p class = "err" v-if="error"> {{ error }}</p>
                <form @submit.prevent ="LoginUser">
                    <div class="mb-3">
                      <label for="username" class="form-label">Username</label>
                      <input type="text" class="form-control" v-model="formData.username" id="username" aria-describedby="userHelp">
                    </div>
                    <div class="mb-3">
                      <label for="password" class="form-label">Password</label>
                      <input type="password" v-model="formData.password" class="form-control" id="password">
                    </div>
                    <input type="submit" class = "btn btn-primary" value="Login"> <br>
                    <!-- <button @click="LoginUser" class="btn btn-primary">Login</button> <br> <br> -->
                    <a href="/register" >Create Account?</a>
                </form>
            </div>
        </div>
    </div>    
</template>




<style>
    #form-body{
        background-color:rgb(145, 193, 223);
    }
    .err{
        color:red;
    }
</style>

