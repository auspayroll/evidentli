<template>
  <div>
        <h2><span v-show="name">{{ name }}</span> </h2><p>

        <flash-message transitionName="slide-fade"></flash-message>
        <div class="nav">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Summary</button>
          <button :class="activePanel == 'cohort' ? 'btn-primary': 'btn-secondary'" @click="activePanel='cohort'">Cohorts</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Fields of analysis</button>
        </div>  


        <transition-group name="fade" mode="out-in" class="panel">

          <div key="summary" class="panel" v-show="activePanel=='summary'">

            <div v-for="field_stat, field_name in stats">
              <h4>{{ field_name }}</h4>
              <table class="table">
                  <tr>
                    <th>Cohort</th>
                    <th>N</th>
                    <th>Mean</th>
                    <th>Std</th>
                    <th>Median</th>
                    <th>IQR</th>
                    <th>Exposures</th>
                    <th>OR</th>
                    </tr>

                    <tr v-for="cohort, cohort_name in field_stat.cohorts">
                    <td>{{ cohort_name }}</td>
                    <td>{{ cohort.n }}</td>
                    <td>{{ cohort.mean | numeric(precision) }}</td>
                    <td>{{ cohort.std | numeric(precision) }}</td>
                    <td>{{ cohort.median | numeric(precision) }}</td>
                    <td>{{ cohort.iqr | numeric(precision) }}</td>
                    <td>{{ cohort.exposures }}/{{ cohort.n }}</td>
                    <td>{{ cohort.ratio | numeric(precision)  }}</td>
                  </tr>
                  
                  <tr>
                    <td>Cohort Comparison</td>
                    <td>{{ field_stat.comparison.n }}</td>
                    <td>{{ field_stat.comparison.mean | numeric(precision) }}</td>
                    <td>{{ field_stat.comparison.std | numeric(precision) }}</td>
                    <td>{{ field_stat.comparison.median | numeric(precision) }}</td>
                    <td>{{ field_stat.comparison.iqr | numeric(precision) }}</td>
                    <td>&nbsp;</td>
                    <td>{{ field_stat.comparison.OR | numeric(precision) }}</td>
                  </tr>
                  
                  <tr>
                    <td>Matched Pairs</td>
                    <td>{{ field_stat.matched_pairs.n }}</td>
                    <td>{{ field_stat.matched_pairs.mean | numeric(precision) }}</td>
                    <td>{{ field_stat.matched_pairs.std | numeric(precision) }}</td>
                    <td>{{ field_stat.matched_pairs.median | numeric(precision) }}</td>
                    <td>{{ field_stat.matched_pairs.iqr | numeric(precision) }}</td>
                    <td></td>
                  </tr> 

              </table>
              
            <p>
              Precision/rounding <br/><input type="number" placeholder="decimal places" v-model="precision" @change="roundPrecision">
            </p>        
            </div>
               
          </div>

          <div key="cohorts" class="panel" v-show="activePanel=='cohort'">

            <h4>Label of analysis</h4>
            <input name="new_cohort" type="text" placeholder="SUMO name" ref="name" v-model="name"> 
            <p/>
            <div v-show="error" class="alert-danger">{{ error }}</div>

            <h4>Cohorts</h4>
            <input type="text" style="font-size:large" v-model="cohort1" placeholder="Cohort 1">

            <input type="text" style="font-size:large" v-model="cohort2" placeholder="Cohort 2">
              
            
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
          </div>


          <div key="pairs" class="panel" v-show="activePanel=='pairs'">
            <p/>
            <h4>Field of analysis</h4>
            <input style="font-size:large; width:90%" v-model="foa" placeholder="eg. Person.provider_id, Person.year_of_birth"></input>
            <p/>
            Precision/rounding <br/><input type="number" placeholder="decimal places" v-model="precision" @blur="roundPrecision">
            <p/>

            Exposure Level <br/><input type="text" style="width:90%" placeholder="category name or threshold value" v-model="exposure_level">
            <p/>
            Category Levels <br/><input type="text" v-model="categories" style="width:90%" placeholder="category threshold values separated by commas eg, 50, 100, 150">
            <p/>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
            <p/>
            
            <h3>OMOP Fields</h3>

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
        
        <canvas v-show="activePanel=='summary' && categorized" id="myChart" width="100%" height="30vh"></canvas>


    </div>

</template>

<script>
  var dirty = false;
  import axios from 'axios';
  import Chart from 'chart.js';
  var myChart;
  var chartLabel;
  var test = 1;

  export default{
    props: ["projectId", "id"],    
    data: function(){
      return {
        cohort1: '',
        cohort2: '',
        categories: '',
        exposure_level: '', 
        name: '', 
        error: '',
        foa: '', 
        activePanel: 'summary',
        schema: null,
        stats:null,
        search: '',
        precision: null,
        categorized: null
      }
    },
    created(){
        this.load()
        this.get_schema()   
    },
    mounted(){
        let ctx = this.$el.querySelector("#myChart");
        if(myChart){
          myChart.destroy();
        }
        var that = this
        myChart = new Chart(ctx, {
          // The type of chart we want to create
          type: 'bar',

          // The data for our dataset
          data: {
              labels: [],
              datasets: [{
                  label: null,
                  backgroundColor: 'rgb(255, 99, 132)',
                  borderColor: 'rgb(255, 99, 132)',
                  data: []
              }]
          },

          // Configuration options go here
          options: {}
        });
        this.getStats()
    },
    computed: {
        chartLabels: function(){
          if(this.categorized){
            return this.categorized.map(x => { return x[0]})
          } else {
            return []
          }
        },
        chartData: function(){
          if(this.categorized){
            return this.categorized.map(x => {return x[1]})
          } else {
            return []
          }
        },
        configsURL: function(){
            return '/projects/' + this.projectId + '/sumo'
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
          var cohorts = this.cohort1 + ', ' + this.cohort2
          var saveObject = { cohorts: cohorts, foa: this.foa, precision: this.precision, 
            name: this.name, _id: this.id, exposure_level: this.exposure_level, 
            categories: this.categories }

          axios.post(this.configsURL, saveObject).then( response => {
            this.activePanel = 'summary'
            this.load()
            this.flash('Sumo saved', 'success', { timeout: 2000 });
            this.calcStats()
          }).catch(error => {
            this.error = error;
          });
      },
      showAddList(column){
        if(column.toLowerCase() == this.foa.toLowerCase){
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
      roundPrecision(){
        this.precision = Math.round(Number(this.precision))
        if(this.precision > 14){
          this.precision = 14
        }
      },
      load(){
        axios.get(this.configsURL + '/' + this.id).then( 
            response => { 
                this.id = response.data._id
                if(response.data.cohorts){
                  var cohorts = response.data.cohorts.split(',')
                  this.cohort1 = cohorts[0].trim()
                  this.cohort2 = cohorts[1].trim()
                  this.categories = response.data.categories
                  this.exposure_level = response.data.exposure_level
                  this.precision = response.data.precision
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
                this.stats = response.data.fields
                this.categorized = response.data.categorized
                console.log(myChart)
                myChart.data.datasets[0].data = this.chartData
                myChart.data.labels = this.chartLabels
                myChart.update()
            }
        ).catch(error => {
          this.error = error
        })
      },
      calcStats(){
        axios.get(this.configsURL + '/' + this.id + '/calc_stats').then( 
            response => { 
                this.stats = response.data.fields
                this.categorized = response.data.categorized
                myChart.data.datasets[0].data = this.chartData
                myChart.data.labels = this.chartLabels
                myChart.update()
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