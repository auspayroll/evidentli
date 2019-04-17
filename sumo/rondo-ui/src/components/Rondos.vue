<template>
  <div>

          <flash-message transitionName="slide-fade"></flash-message>

        <form>

        <router-link :to="{name: 'createRondo', projectId: projectId }" tag="button" class="btn btn-primary">Add RONDO Processor</router-link>
        <div v-show="error" class="alert-danger">{{ error }}</div>

        <p/>
        <table class="table table-striped table-hover">
            <tr><th>Id</th><th>Name</th><th>No. Cohorts</th><th>Matched Pairs</th></tr>
            <tr v-for="rondo in rondos">
                <td>
                    <router-link :to="{ name: 'rondo', params: { id: rondo._id }}">{{ rondo.name || rondo._id}}</router-link>
                </td>        
                <td>
                    {{ rondo.name }}
                </td>
                <td>
                    {{ rondo.cohorts?rondo.cohorts.length:'-' }}
                </td>
                  <td>
                    {{ rondo.matched_pairs?rondo.matched_pairs.length:'-' }}
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
        rondos: [],
        name: '',
        error: ''
      }
    },
    created(){
        axios.interceptors.request.use(request => {
            return request
        });
        axios.get(this.rondosURL).then( 
            response => { 
                this.rondos = response.data
            }
        ).catch(error => {
            this.error = error;
        })
    },
    computed: {
        rondosURL: function(){
            return '/projects/' + this.projectId + '/rondo'
        }
    },
    methods: {
      add(e){
          var new_rondo = { name: this.name, cohorts: [], matched_pairs: []};
          axios.post(this.configsURL, new_rondo).then( response => {
                new_rondo["_id"] = response.data[0];
                this.configs.push(new_rondo);
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