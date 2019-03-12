<template>
  <div>
        <form>
        <h2>Cohorts {{ apiUrl }} #{{ projectId }}#{{ id }}</h2>
        <form v-on:submit="add">
        <input name="new_cohort" type="text" placeholder="cohort name" ref="name" v-model="name"> 
        <button type="button" class="btn btn-primary" @click="add">Add</button> 
        <div v-show="error" class="alert-danger">{{ error }}</div>
        </form>
        <p/>
        <table class="table table-striped table-hover">
            <tr><th>Cohort No.</th><th>Name</th><th>Status</th></tr>
            <tr v-for="cohort in cohorts">
                <td width="20%">{{ cohort.id }}</td>
                <td><router-link to="/devices/update">{{ cohort.n }}</router-link></td>
                <td v-if="cohort.s == 1">Active</td><td v-else>In-active</td>
            </tr>
        </table>

      </form>
    </div>

</template>

<script>
  var dirty = false;

  export default{
    props: ["apiUrl", "projectId", "id"],    
    data: function(){
      return {
        cohorts: [{id: 1, s: 1, n: 'Cohort 1'}, {id: 2, s: 0, n: 'Cohort 2'}],
        name: "", 
        error: ""
      }
    },
    mounted(){
        //this.$refs.name.$el.focus()
        this.$refs.name.focus();
    },
    computed: {
        configURL: function(){
            return this.apiUrl + '/projects/' + this.projectId + '/python-sandox/' + this.id
        }, 
        configsURL: function(){
            return this.apiUrl +  '/projects/' + this.projectid + '/python-sandbox'
        }

    },
    methods: {
      register(){
        this.$router.push('/locations')
      }, 
      getLocation(){
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(this.setPosition);
          } else { 
            console.log('error')
          }
      }, 
      setPosition(position){
        console.log('here');
        this.latitude = position.coords.latitude;
        this.longitude = position.coords.longitude;
      },
      valid_name(){
        const name = this.name.trim();
        if(this.name == ""){
            this.error = "Cohort name is required"
            return false;
        }
        if(this.cohorts.map(x => x.n).includes(this.name)){
            this.error = "Cohort " + this.name + " already exists"
            return false;
        }
        return true;
      },
      add(e){
          console.log(this.configURL);
          e.preventDefault();
          dirty = true;
          this.error = "";
          if(this.valid_name()){
            const key = Object.keys(this.cohorts).length + 1;
            //this.$set(this.cohorts, key, this.name);
            this.cohorts.push({n: this.name, id: key, s: 1});
            this.name = "";
          } else {

          }
          
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