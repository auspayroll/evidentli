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
            <textarea style="height:90px;font-size:large" v-model="cohorts" placeholder="enter cohort names, separated by command, eg. A, B, C etc.."></textarea>

            <p/>
            <h4>Fields of analysis</h4>
            <textarea style="height:90px;font-size:large" v-model="matchedPairs" rows="3" placeholder="enter OMOP field names, seperated by commas"></textarea>

            <p/>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
            <p/>
            <h3>OMOP Fields</h3>
            <div v-if="!schema">Loading...</div>
            <div v-for="table, table_name in schema">
              <div v-for="column in table.columns" class="field-info">
                <strong>{{ table_name | capitalize }}.{{ column.name }}</strong>
                <div>{{ column.description }} <i>Type: {{ column.type }}</i></div>
                <button v-show="showAddList(table_name + '.' + column.name)" class="btn-info float-right" @click="addMatchedPair(table_name + '.' + column.name)">Add</button>
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
        cohorts: '',
        name: '', 
        error: '',
        matchedPairs: '',
        schema: null
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
            var saveObject = { cohorts: this.cohorts, matched_pairs: this.matchedPairs, name: this.name }
            axios.post(this.configsURL, saveObject).then( response => {
              var _id = response.data._id
              console.log(_id)
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
        var mpl = this.matchedPairsList.map(x => { return x.toLowerCase()})
        if(mpl.includes(column.toLowerCase())){
          return false
        }
        return true
      },
      addMatchedPair(column){
        column = column.charAt(0).toUpperCase() + column.slice(1)
        if(this.matchedPairsList.includes(column)){
          return false
        } else {
          if(this.matchedPairs !== '' ){
            this.matchedPairs += ', '
          }
          this.matchedPairs += column
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