<template>
  <div>
        <h1>Sumo <span v-show="name">- {{ name }}</span> </h1><p>
        Project {{ projectId }}
        <flash-message transitionName="slide-fade"></flash-message>
        <div class="nav">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Summary</button>
          <button :class="activePanel == 'cohort' ? 'btn-primary': 'btn-secondary'" @click="activePanel='cohort'">Cohorts</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Fields of analysis</button>
        </div>  

        <transition-group name="fade" mode="out-in" class="panel">

          <div key="summary" class="panel" v-if="activePanel=='summary'">

            <h3 style="margin: auto">Label of analysis</h3>
            <div v-for="field_stat, field_name in stats">
              <h4>{{ field_name }}</h4>
              <table class="table">
                  <tr>
                    <th>Cohort</th>
                    <th>Mean</th>
                    <th>Std</th>
                    <th>Median</th>
                    <th>IQR</th>
                    <th>OR</th>
                    </tr>
                    <tr v-for="cohort, cohort_name in field_stat.cohorts">
                    <td>{{ cohort_name }}</td>
                    <td>{{ cohort.mean }}</td>
                    <td>{{ cohort.std }}</td>
                    <td>{{ cohort.median }}</td>
                    <td>{{ cohort.iqr }}</td>
                    <td>{{ cohort.or  }}</td>
                  </tr>
                  
                  <tr>
                    <td>Difference</td>
                    <td>{{ field_stat.comparison.mean }}</td>
                    <td>{{ field_stat.comparison.std }}</td>
                    <td>{{ field_stat.comparison.median }}</td>
                    <td>{{ field_stat.comparison.iqr }}</td>
                    <td>{{ field_stat.comparison.or }}</td>
                  </tr>
                  
                  <tr>
                    <td>Matched Pairs</td>
                    <td>{{ field_stat.matched_pairs.mean }}</td>
                    <td>{{ field_stat.matched_pairs.std }}</td>
                    <td>{{ field_stat.matched_pairs.median }}</td>
                    <td>{{ field_stat.matched_pairs.iqr }}</td>
                    <td>{{ field_stat.matched_pairs.or | 1 }}</td>
                  </tr> 

              </table>

              <span v-for="stat in field_stat"

                 <p>&nbsp;</p>
            </div>
               
          </div>


          <div key="cohorts" class="panel" v-if="activePanel=='cohort'">

            <h4>Sumo Name</h4>
            <input name="new_cohort" type="text" placeholder="SUMO name" ref="name" v-model="name"> 
            <p/>
            <div v-show="error" class="alert-danger">{{ error }}</div>

            <h4>Cohorts</h4>
            <textarea style="height:90px;font-size:large" v-model="cohorts" placeholder="enter cohort labels/names, separated by commas, eg. Cohort1, Cohort2, Cohort 3; ">
              
            </textarea>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
          </div>


          <div key="pairs" class="panel" v-if="activePanel=='pairs'">
            <p/>
            <h4>Fields of analysis</h4>
            <textarea style="height:90px;font-size:large" v-model="foa" rows="3" placeholder="enter field names, seperated by commas, eg. Person.provider_id, Person.year_of_birth"></textarea>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
            <p/>
            
            <h3>OMOP Fields <input type="text" placeholder="search" v-model="search"></h3>

            <div v-if="!schema">Loading...</div>
            <div v-for="table, table_name in schema">
              <div v-for="column in table.columns" class="field-info">
                <strong>{{ table_name | capitalize }}.{{ column.name }}</strong>
                <div>{{ column.description }} <i>Type: {{ column.type }}</i></div>
                <button v-show="showAddList(table_name + '.' + column.name)" class="btn-info float-right" @click="addFoa(table_name + '.' + column.name)">Add</button>
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
        foa: '', 
        activePanel: 'summary',
        schema: null,
        stats:null,
        search: ''
      }
    },
    created(){
        this.load()
        this.get_schema()
        this.getStats()
    },
    mounted(){
        //this.$refs.name.$el.focus()
        //this.$refs.name.focus();
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/sumo'
        },
        foaList: function(){
            if(!this.foa){
              return []
            } else {
              try{
                return this.foa.split(',').map(pair => { return pair.trim()})
              } catch(err){
                console.log(err)
                console.log(this.foa)
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
            var saveObject = { cohorts: this.cohorts, foa: this.foa, 
              name: this.name, _id: this.id }

            axios.post(this.configsURL, saveObject).then( response => {
              this.activePanel = 'summary'
              this.load()
              this.flash('Sumo saved', 'success', { timeout: 2000 });
              this.getStats()
            }).catch(error => {
              this.error = error;
            });
      },
      showAddList(column){
        var mpl = this.foaList.map(x => { return x.toLowerCase()})
        if(mpl.includes(column.toLowerCase())){
          return false
        }
        return true
      },
      addFoa(column){
        column = column.charAt(0).toUpperCase() + column.slice(1)
        if(this.foaList.includes(column)){
          return false
        } else {
          if(this.foa !== '' ){
            this.foa += ', '
          }
          this.foa += column
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
                if(response.data.foa){
                  this.foa = response.data.foa.toString()
                }
                this.name = response.data.name || ''
            }
        ).catch(error => {
          this.error = error
        })
      },
      getStats(){
        axios.get(this.configsURL + '/' + this.id + '/stats').then( 
            response => { 
                this.stats = response.data
                console.log(this.stats)
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