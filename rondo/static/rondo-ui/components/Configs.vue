<template>
  <div>
        <form>
            <h4>-Rondo Configurations-</h4>

        <form v-on:submit="add">
        <input name="new_cohort" type="text" placeholder="processor name" ref="name" v-model="name"> 
        <button type="button" class="btn btn-primary" @click="add">Add Cohort Processor</button> 
        <div v-show="error" class="alert-danger">{{ error }}</div>
        </form>
        <p/>
        <table class="table table-striped table-hover">
            <tr><th>Id</th><th>Name</th><th>No. Cohorts</th></tr>
            <tr v-for="config in configs">
                <td>
                    <router-link :to="{ name: 'cohort', params: { id: config._id }}">{{config.name || config._id}}</router-link>
                </td>        
                <td>
                    {{ config.name }}
                </td>
                <td>
                    {{ config.no_cohorts }}
                </td>
            </tr>
        </table>

      </form>
      <code>{{ configs }}</code>
    </div>

</template>

<script>
  import axios from 'axios';
  var dirty = false;

  export default{
    props: ["projectId"],    
    data: function(){
      return {
        configs: [],
        name: '',
        error: ''
      }
    },
    created(){
        axios.interceptors.request.use(request => {
            console.log('Starting Request', request)
            return request
        });
        axios.get(this.configsURL).then( 
            response => { 
                this.configs = response.data.filter(config => config.type === 'rondo')  
                console.log(response.data)
            }
        ).catch(error => {
            this.error = error;
        })
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/python-sandbox'
        }
    },
    methods: {
      add(e){
          var new_cohort = { name: this.name, no_cohorts: 0, cohorts: [], matched_pairs: [], type: 'rondo'};
          axios.post(this.configsURL, 
            [new_cohort]).then( response => {
                new_cohort["_id"] = response.data[0];
                this.configs.push(new_cohort);
          })
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