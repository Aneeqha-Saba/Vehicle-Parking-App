<script>
// export default {
//     methods: {
//         toLogin: function() {
//             this.$router.push('/login')
//         }
//     }
// }
</script>

<template>
    <div class="container-fluid forms">
        <div class="row align-items-center">
            <div class="col-8 content"></div>
            <div class="col-4 text-center">
                <div class="m-3">
                    <button @click="this.$router.push('/login')" class="btn bg-success-subtle btns">Login</button>
                </div>
                <div class="m-3">
                    <button @click="this.$router.push('/register')" class="btn bg-primary-subtle btns">Sign Up</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
    .content{
        background-image: url("../assets/cover.png");
        background-size: 100% 100%;
        height: 85vh;
    }
    .forms{
        background-color: #92efde;
    }
    .btns{
        width: 33%;
    }
</style>