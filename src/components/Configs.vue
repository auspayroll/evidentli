<template>
  <div>
        <form>
        <h2>Configs for Project {{ projectId }}</h2>

        <table class="table table-striped table-hover">
            <tr><th>Cohort No.</th><th>Name</th><th>Status</th></tr>
            <tr v-for="config in configs">
                <td width="20%">{{ config.id }}</td>
                <td><router-link>{{ config.id }}</router-link></td>
            </tr>
        </table>
        <button @click="add">SEnd</button>

      </form>
    </div>

</template>

<script>
  import axios from 'axios';
  var dirty = false;

  export default{
    props: ["apiUrl", "projectId"],    
    data: function(){
      return {
        configs: [],
      }
    },
    created(){
        const url = this.getConfigsURL;
        //console.log(url);
        //axios.defaults.headers.common['content-type'] = "application/json";
        //axios.get(this.getConfigsURL).then(response => console.log(response));
    },
    computed: {
        getConfigsURL: function(){
            return this.apiUrl + '/projects/' + this.projectId + '/python-sandbox'
        }, 
        createConfigURL: function(){
            return this.apiUrl +  '/projects/' + this.projectid + '/python-sandbox'
        }

    },
    methods: {
      add(e){
        const instance = axios.create({
            baseURL: this.getConfigsURL
        });
        instance.interceptors.request.use(request => {
            console.log('Starting Request', request)
            return request
        });
        //axios.get(this.getConfigsURL, { headers: { 'Content-Type': 'application/json' }}).then(response => console.log(response));
        //axios.get('https://jsonplaceholder.typicode.com/todos/1', { headers: { 'User-Agent': 'tasty_cookie=strawberry' }}).then(response => console.log(response));
        instance.get('').then( response => console.log(response))
      }
    }

  }

</script>

<style scoped>
  .coord{
    width: auto;
    display: inline;
  }
  h2 {
    float: none;
  }

  DIV .alert-danger{
      padding: 6px;
      border-radius: 4px;
  }

</style>