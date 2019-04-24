<template>
  <div>
        
        <flash-message transitionName="slide-fade"></flash-message>

        <form>

        <router-link :to="{name: 'createSumo', projectId: projectId }" tag="button" class="btn btn-primary">Add SUMO Processor</router-link>
        <div v-show="error" class="alert-danger">{{ error }}</div>

        <p/>
        <table class="table table-striped table-hover">
            <tr>
            <th>Label</th>
            <th>Field of analysis</th>
            <th>No. Cohorts</th>
            </tr>
            <tr v-for="sumo in sumos">
                <td>
                    <router-link :to="{ name: 'sumo', params: { id: sumo._id }}">{{ sumo.name || sumo._id}}</router-link>
                </td>        
                <td>
                    {{ sumo.foa }}
                </td>
                <td>
                    {{ sumo.cohorts }}
                </td>
            </tr>
        </table>

      </form>
    </div>

</template>

<script>
  import axios from 'axios';
  var dirty = false;

  export default{
    props: ["projectId"],    
    data: function(){
      return {
        sumos: [],
        name: '',
        error: ''
      }
    },
    created(){
        axios.interceptors.request.use(request => {
            return request
        });
        axios.get(this.sumosURL).then( 
            response => { 
                this.sumos = response.data
            }
        ).catch(error => {
            this.error = error;
        })
    },
    computed: {
        sumosURL: function(){
            return '/projects/' + this.projectId + '/sumo'
        }
    },
    methods: {
      add(e){
          var new_sumo = { name: this.name, cohorts: [], matched_pairs: []};
          axios.post(this.configsURL, new_sumo).then( response => {
                new_sumo["_id"] = response.data[0];
                this.configs.push(new_sumo);
          })
      }, 
      csvLength(csv){
        return csv.split(",").length
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