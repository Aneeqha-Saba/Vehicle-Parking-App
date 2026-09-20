import {createWebHistory, createRouter, stringifyQuery} from 'vue-router';
import Content from './components/Content.vue';
import LoginPage from './components/LoginPage.vue';
import RegisterPage from './components/RegisterPage.vue';
import Aduser from './components/Aduser.vue';
import dashboard from './components/dashboard.vue';
import search from './components/search.vue';
import summary from './components/summary.vue';
import release from './components/release.vue';
import reserve from './components/reserve.vue';
import create_lot from './components/create_lot.vue';
import edit_lot from './components/edit_lot.vue';
import delete_lot from './components/delete_lot.vue';
import profile from './components/profile.vue';

const routes= [
    { path: "/", component: Content},
    { path: "/content", component: Content},
    { path: "/login", component: LoginPage},
    { path: "/register", component: RegisterPage},
    { path: "/user", component: Aduser},
    { path: "/dashboard", component: dashboard},
    { path: "/search", component: search},
    { path: "/summary", component: summary}, 
    { path: "/user/reserve/:lot_id", component:reserve},
    { path: "/user/release/:spot_id", component: release},
    { path: "/admin/create_lot", component: create_lot},
    { path: "/admin/edit_lot/:lot_id", component: edit_lot},
    {path: "/admin/delete_lot/:lot_id", component: delete_lot},
    {path: "/profile", component: profile}
    ]



export const router = createRouter({
    history: createWebHistory(),
    routes // --> routes: routes
})

// this.$router.go(0)

