<template>
  <div>

        <span>- <strong>RONDO</strong> {{ id }} -</span>
        <p/>
        <div class="nav">
          <button :class="panel_toggle ? 'btn-primary': 'btn-secondary'" @click="panel_toggle=true">Cohorts</button>
          <button  :class="panel_toggle ? 'btn-secondary': 'btn-primary'" @click="panel_toggle=false">Matched Pairs</button>
        </div>

        <transition name="fade" mode="out-in" class="panel">
          <div key="cohort_panel" class="panel" v-if="panel_toggle">
            <h4>- Cohorts -</h4>
            <form v-on:submit="add">
            <input name="new_cohort" type="text" placeholder="cohort name" ref="name" v-model="name"> 
            <button type="button" class="btn btn-primary" @click="add">Add</button> 
            <div v-show="error" class="alert-danger">{{ error }}</div>
            </form>
            
            <p/>
            <table class="table table-striped table-hover" v-show="cohorts.length > 0">
                <tr><th>Cohort No.</th><th>Name</th><th>Active</th></tr>
                
                <tr v-for="cohort in cohorts" :key="cohort.id">
                    <td width="20%">{{ cohort.id }}</td>
                    <td><input :id="cohort.id" type="text" :value="cohort.name" name="" @change="nameChange"></td>
                    <td><input :id="cohort.id" type="checkbox" :checked="cohort.active" @change="statusChange"></td>
                </tr>
            </table>
          </div>

          <div key="matched_panel" v-if="!panel_toggle" class="panel">
            <h4>-Matched Pairs-</h4>
            <ul>
                <li v-for="mp in matchedPairNames"><input type="checkbox" :checked="matchedPairs.includes(mp)" :value="mp" @change="updateMatchedPairs"> {{ mp }}</li>
            </ul>
          </div>
        </transition>

  <code>
  {{ saveObject }}
  </code>
    </div>

</template>

<script>
  var dirty = false;
  import axios from 'axios';
  //const matchedPairs = ['age', 'gender'];

  export default{
    props: ["projectId", "id"],    
    data: function(){
      return {
        cohorts: [],
        config_name: '', 
        name: '', 
        error: '',
        panel_toggle: true, 
        matchedPairNames: ['age', 'gender', 'length-of-stay'], 
        matchedPairs: [], 
        no_cohorts: 0
      }
    },
    created(){
        var get_url = this.configsURL + '/' + this.id;
        console.log(get_url)
        axios.get(get_url).then( 
            response => { 
                this.id = response.data._id;
                this.cohorts = response.data.cohorts;
                this.matchedPairs = response.data.matched_pairs;
                this.no_cohorts = response.data.no_cohorts;
            }
        ).catch(error => {
          this.error = error;
        })
    },
    mounted(){
        //this.$refs.name.$el.focus()
        this.$refs.name.focus();
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/rondo'
        },
        saveObject: function(){ return { _id: this.id, name: this.config_name, 
          cohorts: this.cohorts, matched_pairs: this.matchedPairs, no_cohorts: this.no_cohorts }
        }

    },
    methods: {
      updateMatchedPairs(e){
        if(e.target.checked && !this.matchedPairs.includes(e.target.value)){
            this.matchedPairs.push(e.target.value)
        } else {
          this.matchedPairs.splice(this.matchedPairs.indexOf(e.target.value),1)
        }
        console.log(this.matchedPairs)
        this.save()
      },
      nameChange(e){
        var cohort = this.getCohort(e.target.id);
        var original_value = cohort.name;
        if(e.target.value.trim() === '' ){
          e.target.value = original_value;
        } else {
          cohort.name = e.target.value;
          axios.post(this.configsURL, [this.saveObject]).then( response => {
            console.log(response);
          }).catch(error => {
            this.error = error;
            this.cohorts[parseInt(e.target.id)-1].name = original_value;
          });
        }
      },
      getCohort(id){
        var cohort = this.cohorts.filter(cohort => cohort.id == id )
        if(cohort.length == 1){
          return cohort[0]
        } else {
          return null
        }
      },
      statusChange(e){
        var cohort = this.getCohort(e.target.id)
        cohort.active = e.target.checked;
        this.no_cohorts = this.cohorts.filter(cohort => cohort.active).length
        axios.post(this.configsURL, [this.saveObject]).then( response => {
          console.log(response);
        }).catch(error => {
          this.error = error;
          cohort.active = !e.target.checked;
        });
      },

      valid_name(){
        const name = this.name.trim();
        if(this.name == ""){
            this.error = "Cohort name is required"
            return false;
        }
        if(this.cohorts.map(cohort => cohort.name).includes(this.name)){
            this.error = "Cohort " + this.name + " already exists"
            return false;
        }
        return true;
      },
      add(e){
          e.preventDefault();
          dirty = true;
          this.error = "";
          if(this.valid_name()){
            const key = this.cohorts.length + 1;
            //this.$set(this.cohorts, key, this.name);
            this.cohorts.push({name: this.name, id: key, active: true});
            this.save();
            this.name = "";
          } else {

          }     
      },
      save(){
            axios.post(this.configsURL, [this.saveObject]).then( response => {
            }).catch(error => {
              this.error = error;
            });
      }
    }
  }

</script>

<style scoped>
  h2 {
    float: none;
  }

  DIV .alert-danger{
      padding: 6px;
      border-radius: 4px;
  }

  .nav{
    margin-bottom:20px;
  }

</style>