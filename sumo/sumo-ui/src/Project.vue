<template>

    <div id="app">
    <div id="logo_frame"></div>
    <h1>Sumo</h1>
    Project: {{ id }}
    <div id="content">
      <div id="sidebar">
        <h3>{{ id }}</h3> 
        <router-link :to="{ name: 'sumos', params: { projectId: this.id } }">SUMOS</router-link>
        <!--<router-link :to="{ name: 'sumos' }">SUMO</router-link>-->
       
      </div>
      
      <div id="main">

        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
        
        </div>
    </div>

  </div>

</template>


<script>
  
  import axios from 'axios';
  axios.defaults.baseURL = process.env.VUE_APP_REMOTE
  export default {
    props: ['projectId'], 
    data(){
      //console.log(JSON.stringify(this.$route.params))
      var _id = this.$route.params.projectId || this.projectId || 'test_michael2'
      return {
        id: _id
      }
    },
    created(){
      this.$router.push({ name: 'sumos', params: { projectId: this.id } })
    }
  }
  
</script>

<style>


</style>
