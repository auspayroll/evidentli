<template>
  <div>

        <flash-message transitionName="slide-fade"></flash-message>
        <div class="nav">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Summary</button>
          <button :class="activePanel == 'cohort' ? 'btn-primary': 'btn-secondary'" @click="activePanel='cohort'">Cohorts</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Matched Pairs</button>
        </div>
        

        <transition-group name="fade" mode="out-in" class="panel">

          <div key="summary" class="panel" v-if="activePanel=='summary'">

            <h4>Rondo Name</h4>
            {{ name || '-' }}
            <hr/>
            <h4>Cohorts</h4>
              <li v-for="mp in cohortList"><button class="btn-info tag">{{ mp }}</button></li>
            <hr/>
            <h4>Matched Pairs</h4>
            <ul>
              <li v-for="mp in matchedPairsList"><button class="btn-info tag">{{ mp }}</button></li>
            </ul>

          </div>


          <div key="cohorts" class="panel" v-if="activePanel=='cohort'">

            <h4>Rondo Name</h4>
            <input name="new_cohort" type="text" placeholder="RONDO name" ref="name" v-model="name"> 
            <p/>
            <div v-show="error" class="alert-danger">{{ error }}</div>

            <h4>Cohorts</h4>
            <textarea style="height:90px;font-size:large" v-model="cohorts" placeholder="enter cohort labels/names, separated by commas, eg. Cohort1, Cohort2, Cohort 3; ">
              
            </textarea>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
          </div>


          <div key="pairs" class="panel" v-if="activePanel=='pairs'">
            <p/>
            <h4>Matched Pairs</h4>
            <textarea style="height:90px;font-size:large" v-model="matchedPairs" rows="3" placeholder="enter field names, seperated by commas, eg. Person.provider_id, Person.year_of_birth"></textarea>
            <!--<input type="checkbox" v-model="matchByCohort"> Match by Cohort-->
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
          
        </transition-group>

    </div>

</template>

<script>
  var dirty = false;
  import axios from 'axios';

  export default{
    props: ["projectId", "id"],    
    data: function(){
      return {
        cohorts: '',
        name: '', 
        error: '',
        matchByCohort: false,
        matchedPairs: '', 
        activePanel: 'summary',
        schema: null,
      }
    },
    created(){
        this.load()
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
                console.log(err)
                console.log(this.matchedPairs)
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
              match_by_cohort: this.matchByCohort, name: this.name, _id: this.id }

            axios.post(this.configsURL, saveObject).then( response => {
              //this.$router.push('/projects/' + this.projectId + '/rondos')
              this.activePanel = 'summary'
              this.load()
              this.flash('Rondo saved', 'success', { timeout: 2000 });
            }).catch(error => {
              this.error = error;
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
        if(this.matchedPairsList.includes(column)){
          return false
        } else {
          if(this.matchedPairs !== '' ){
            this.matchedPairs += ', '
          }
          this.matchedPairs += column
        }
      },
      load(){
        axios.get(this.configsURL + '/' + this.id).then( 
            response => { 
                this.id = response.data._id
                this.cohorts = response.data.cohorts.toString()
                this.matchedPairs = response.data.matched_pairs.toString()
                this.matchByCohort = response.data.match_by_cohort
                this.name = response.data.name || ''
            }
        ).catch(error => {
          this.error = error
        })
      },
      get_schema(){
        axios.get( '/projects/' + this.projectId + '/schema').then( 
            response => { 
                this.schema = response.data.tables
            }
        ).catch(error => {
          
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