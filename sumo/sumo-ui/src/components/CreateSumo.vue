<template>
  <div>

        <h1>New Sumo</h1>
        <p/>
   
          <div key="cohort_panel" class="panel">

            <h4>Label of analysis</h4>
            <input name="new_cohort" type="text" placeholder="SUMO name" ref="name" v-model="name"> 
            <p/>
            <div v-show="error" class="alert-danger">{{ error }}</div>
            
            <h4>Cohorts</h4>
            <input type="text" style="font-size:large" v-model="cohort1" placeholder="Cohort 1">

            <input type="text" style="font-size:large" v-model="cohort2" placeholder="Cohort 2">

            <p/>
            <h4>Field of analysis</h4>
            <input style="font-size:large; width:90%" v-model="foa" placeholder="eg. Person.year_of_birth"></input>

            <p/>

            Exposure Level <br/><input type="text" style="width:90%" placeholder="category name or threshold value" v-model="exposure_level">
            <p/>
            Category Levels <br/><input type="text" v-model="categories" style="width:90%" placeholder="category threshold values separated by commas eg, 50, 100, 150">
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
            <p/>
            <h3>OMOP Fields</h3>
            <div v-if="!schema">Loading...</div>
            <div v-for="table, table_name in schema">
              <div v-for="column in table.columns" class="field-info">
                <strong>{{ table_name | capitalize }}.{{ column.name }}</strong>
                <div>{{ column.description }} <i>Type: {{ column.type }}</i></div>
                <button class="btn-info float-right" @click="addFoa(table_name + '.' + column.name)">Add</button>
              </div>
            </div>

          </div>      
  
    </div>

</template>

<script>
  var dirty = false;
  import axios from 'axios';

  export default{
    props: ["projectId"],    
    data: function(){
      return {
        cohort1: '',
        cohort2: '',
        foa: '',
        name: '', 
        error: '',
        matchedPairs: '',
        schema: null,
        categories: '',
        exposure_level: ''
      }
    },
    mounted(){
        //this.$refs.name.$el.focus()
        //this.$refs.name.focus();
    },
    computed: {
      configsURL: function(){
          return '/projects/' + this.projectId + '/sumo'
      },
      matchedPairsList: function(){
          if(!this.matchedPairs){
            return []
          } else {
            try{
              return this.matchedPairs.split(',').map(pair => { return pair.trim()})
            } catch(err){
              console.log(err)
              console.log(this.matchedPairs)
              return []
            }
          }
      }
    },
    created(){
      this.get_schema()
    },
    methods: {
      save(){
            var cohorts = this.cohort1 + ', ' + this.cohort2
            var saveObject = { cohorts: cohorts, foa: this.foa, 
              name: this.name, exposure_level: this.exposure_level, categories: this.categories }
            axios.post(this.configsURL, saveObject).then( response => {
              var _id = response.data._id
              this.flash('Sumo saved', 'success', { timeout: 2000 });
              this.$router.push({name: 'sumo', params: { id: _id } })
            }).catch(error => {
              this.error = error;
            });
      },
      get_schema(){
        axios.get( '/projects/' + this.projectId + '/schema').then( 
            response => { 
                this.schema = response.data.tables
            }
        ).catch(error => {
          
        })
      },
      showAddList(column){
        console.log('here')
        if(column.toLowerCase() == this.foa.toLowerCase()){
          return false
        }
        return true
      },
      addFoa(column){
        column = column.charAt(0).toUpperCase() + column.slice(1)
        if(column.toLowerCase() == this.foa.toLowerCase){
          return false
        } else {
          this.foa = column
          return true
        }
      },

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

  button {
    margin-right: 1px;
  }

  textarea {
    width: 100%;
    height: 300px;
  }

</style>