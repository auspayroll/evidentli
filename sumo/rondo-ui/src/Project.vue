<template>

    <div id="app">
    <div id="logo_frame"></div>
    Project: {{ id }}
    <div id="content">
      <div id="sidebar">
        <h3>{{ id }}</h3> 
        <router-link :to="{ name: 'rondos', params: { projectId: this.id } }">RONDOS</router-link>
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
    props: ['project_id'], 
    data(){
      //console.log(JSON.stringify(this.$route.params))
      var _id = this.$route.params.projectId || this.project_id || 'test_michael2'
      return {
        id: _id
      }
    },
    created(){
      this.$router.push({ name: 'rondos', params: { projectId: this.id } })
    }
  }
  
</script>

<style>


</style>
