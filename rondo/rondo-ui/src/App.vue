<template>
  <div id="app">
    <h1>RONDO</h1>
    <Project project_id="test_michael2" />

  </div>
</template>

<script>
  import axios from 'axios'
  import Project from './Project.vue'
  axios.defaults.baseURL = process.env.VUE_APP_REMOTE


  export default {
    components: { Project }
  }
    
  </script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
}

button {
  margin-bottom: 2px;
}

#main{
  text-align:left;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

      .alert-success{
        padding: 4px;
      }
      .wrapper {

      }

      #footer {
        border:1pt green solid;
      }

      #sidebar {
        padding-top: 15px;
        background: #eaedeb;
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 18%;
      }

      #sidebar a{
        display: block;
        border: 0pt black solid;
        padding: 1em;
        background: #fff;
        margin: 1px;
      }

      #sidebar a.router-link-active{
        background: #598c6d;
        color: white;
        font-weight: bold;
      }

      .btn-success{
        font-weight: bold;
      }



      #sidebar a:hover{
        background: #598c6d;
        color: white;
        font-weight: bold;
        text-decoration: none;
      }

      #content {
        margin-left: 18%;
      }

      #footer {
        background: grey;
      }

      div {
      }

      #register_btn{
        float:right;
      }

      h2{ float:left }

      #main{
        padding: 2%;
      }

      #logo_frame {
        background: #000;

      }

  .panel{
    border: 0pt #cccccc solid;
    border-radius: 5px;
    padding: 6px;
    margin-bottom: 10px;
    padding-bottom: 15px;
  }

  .fade-enter {
    opacity: 0;
  }

  .fade-enter-active {
    transition: opacity 0.2s;
  }

  .fade-leave-active {
    transition: opacity 0.2s;
    opacity: 0;
  }

</style>
