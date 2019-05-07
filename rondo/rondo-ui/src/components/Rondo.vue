<template>
  <div>
    
        <h1>Rondo</h1><p>
        Project {{ projectId }}
        <flash-message transitionName="slide-fade"></flash-message>
        <div class="nav" v-if="id">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Summary</button>
          <button :class="activePanel == 'cohort' ? 'btn-primary': 'btn-secondary'" @click="activePanel='cohort'">Cohorts</button>
        </div>   

        <transition-group name="fade" mode="out-in" class="panel">

          <div key="summary" class="panel" v-if="activePanel=='summary' && id">
            <h4>Rondo Name</h4>
            {{ name || '-' }}
            <hr/>
            
            <h4><span v-show="random">Random</span> Cohorts</h4>
              <li v-for="mp in cohortList"><button class="btn-info tag">{{ mp }}</button></li>
            <hr/>
            <div v-show="!random">
              <h4>Matched Pairs</h4>
              <ul>
                <li v-for="mp in matchedPairsList"><button class="btn-info tag">{{ mp }}</button></li>
              </ul>
            </div>
          </div>

          <div key="cohorts" class="panel" v-if="activePanel=='cohort'">

              <h4>Rondo Name</h4>
              <input name="new_cohort" type="text" placeholder="RONDO name" ref="name" v-model="name"> 
              <p/>
              <div v-show="error" class="alert-danger">{{ error }}</div>

              <h4>Cohorts</h4>
              <input style="font-size:large; width:90%" v-model="cohorts" placeholder="enter cohort labels/names, separated by commas, eg. Cohort1, Cohort2, Cohort 3; ">
              <p>
              <input type="checkbox" v-model="random"> Allocate as random cohorts
              </p>
              <button name="save" type="button" class="btn-success" @click="save" v-show="random==true">Save</button>

              <div key="pairs" class="panel" v-show="random==false">
                <p/>
                <h4>Matched Pairs</h4>
                <input style="width:90%;font-size:large" v-model="matchedPairs" rows="3" placeholder="enter field names, seperated by commas, eg. Person.provider_id, Person.year_of_birth">
                <p/>
                <p>
                <button name="save" type="button" class="btn-success" @click="save">Save</button></p> 
                
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
          
        </transition-group>

    </div>

</template>

<script>
  var dirty = false;
  import axios from 'axios';
  const timeout = 2000

  export default{
    props: ["projectId", "id"],    
    data: function(){
      var initPanel = this.id ? 'summary' : 'cohort'
      return {
        cohorts: '',
        name: '', 
        error: '',
        matchedPairs: '', 
        activePanel: initPanel,
        schema: null,
        random: false
      }
    },
    created(){
      if(this.id){
        this.load()
      }
      this.get_schema()
    },
    mounted(){
        //this.$refs.name.$el.focus()
        //this.$refs.name.focus();
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/rondo'
        },
        matchedPairsList: function(){
            if(!this.matchedPairs){
              return []
            } else {
              try{
                return this.matchedPairs.split(',').map(pair => { return pair.trim()})
              } catch(err){
                return []
              }
            }
        },
        cohortList: function(){
          if(!this.cohorts){
            return []
          } else {
            try {
              return this.cohorts.split(',').map(cohort => { return cohort.trim()})
            } catch(err) {
              console.log(err)
              console.log(this.cohorts)
              return []
            }
          }
        }
    },
    methods: {
      save(){
            var saveObject = { cohorts: this.cohorts, matched_pairs: this.matchedPairs, 
              name: this.name, _id: this.id, random: this.random }

            axios.post(this.configsURL, saveObject).then( response => {
              this.flash('Rondo saved', 'success', { timeout });
              this.activePanel = 'summary'
              if(!this.id){
                this.$router.push('/projects/' + this.projectId + '/rondos/' + response.data._id)
              }
            }).catch(error => {
              this.flash(error, 'error', { timeout });
            });
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
          return true
        }
      },
      load(){
        axios.get(this.configsURL + '/' + this.id).then( 
            response => { 
                this.id = response.data._id
                if(response.data.cohorts){
                  this.cohorts = response.data.cohorts.toString()
                }
                if(response.data.matched_pairs){
                  this.matchedPairs = response.data.matched_pairs.toString()
                }
                this.random = response.data.random
                this.name = response.data.name || ''
            }
        ).catch(error => {
          this.flash(error, 'error', { timeout });
        })
      },
      get_schema(){
        axios.get( '/projects/' + this.projectId + '/schema').then( 
            response => { 
                this.schema = response.data.tables
            }
        ).catch(error => {
          this.flash(error, 'error', { timeout });
        })
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

  button {
    margin-right: 1px;
  }

  textarea {
    width: 100%;
    height: 300px;
  }

</style>