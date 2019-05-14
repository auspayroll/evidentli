<template>
  <div>
        <h2><span v-show="name">{{ name }}</span> </h2><p>

        <flash-message transitionName="slide-fade"></flash-message>
        <div class="nav">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Summary</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Edit</button>
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
                  
                  <tr><th colspan="5">Cohort Difference</th></tr>
                  <tr v-for="stat, cohort_pair in field_stat.comparison">
                    <td>{{ cohort_pair }}</td>
                    <td>&nbsp;</td>
                    <td>{{ stat.mean | numeric(precision) }}</td>
                    <td>{{ stat.std | numeric(precision) }}</td>
                    <td>{{ stat.median | numeric(precision) }}</td>
                    <td>{{ stat.iqr | numeric(precision) }}</td>
                    <td>&nbsp;</td>
                    <td>{{ stat.OR | numeric(precision) }}</td>
                  </tr>
                  
                  <tr><th colspan="5">Matched Pairs</th></tr>
                  <tr v-for="stat, cohort_pair in field_stat.matched_pairs">
                    <td>{{ cohort_pair }}</td>
                    <td>{{ stat.n }}</td>
                    <td>{{ stat.mean | numeric(precision) }}</td>
                    <td>{{ stat.std | numeric(precision) }}</td>
                    <td>{{ stat.median | numeric(precision) }}</td>
                    <td>{{ stat.iqr | numeric(precision) }}</td>
                    <td></td>
                  </tr> 

              </table>       
            <p>
              Precision/rounding <br/><input type="number" placeholder="decimal places" v-model="precision" @change="roundPrecision">
            </p>        
            </div>        
          </div>

          <div key="pairs" class="panel" v-show="activePanel=='pairs'">
            <h4>Cohorts</h4>
            <input type="text" style="font-size:large;width:90%" v-model="cohorts" placeholder="Enter cohort labels separated by spaces eg A, B">
            <p/>
            <h4>Field of analysis</h4>
            <input style="font-size:large; width:90%" v-model="foa" placeholder="eg. Person.year_of_birth"></input>
            <p/>
            
            <p>&nbsp;</p>

            <p>Exposure Level <br/><input type="text" style="width:90%" placeholder="category name or threshold value" v-model="exposure_level"></p>

            <p>Distribution Levels <br/><input type="text" v-model="categories" style="width:90%" placeholder="distribution threshold values separated by commas eg, 50, 100, 150">
            </p>

            <p>Precision/rounding <br/><input type="number" placeholder="decimal places" v-model="precision" @blur="roundPrecision"></p>
            <button name="save" type="button" class="btn-success" @click="save">Save</button>
            <p/>
            
            <p>&nbsp;</p>
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
          
        </transition-group>
        <canvas id="myChart" v-show="activePanel=='summary' && chartData.length > 0" width="100%" height="30vh"></canvas>
        
        <div v-show="activePanel=='summary' && chartData.length > 0">
          <button class="btn-secondary" @click="updateChartCohort('total')">All Cohorts</button><button class="btn-secondary" v-for="cohort in cohortList" @click="updateChartCohort(cohort)">{{ cohort }}</button>
        </div>
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
        cohorts: '',
        chartCohort: 'total',
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
        distribution: null,
        ordinals: ''
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
          if(this.distribution == null){
            return []

          } else {
            var fieldname = Object.keys(this.distribution)[0]
            var field_category = this.distribution[fieldname][this.chartCohort]
            return field_category.map(x => { return x[0]})
          }
        },
        chartData: function(){
          if(!this.distribution){
            return []
          } else {
            var fieldname = Object.keys(this.distribution)[0]
            var field_category = this.distribution[fieldname][this.chartCohort]
            if(field_category){
              return field_category.map(x => {return x[1]})
            } else {
              return []
            }
            
          }
        },
        configsURL: function(){
            return '/projects/' + this.projectId + '/sumo'
        },
        cohortList: function(){
          if(!this.cohorts){
            return []
          } else {
            return this.cohorts.split(',').map( x => x.trim() )
          }
        }
    },
    methods: {
      save(){
          var saveObject = { cohorts: this.cohorts, foa: this.foa, precision: this.precision, 
            name: this.name, _id: this.id, exposure_level: this.exposure_level, 
            categories: this.categories }

          axios.post(this.configsURL, saveObject).then( response => {
            this.activePanel = 'summary'
            this.load()
            this.flash('Sumo saved', 'success', { timeout: 2000 });
          }).catch(error => {
            this.error = error;
          });
      },
      updateChartCohort(cohort){
        console.log(cohort)
        this.chartCohort = cohort
        myChart.data.datasets[0].data = this.chartData
        myChart.data.labels = this.chartLabels
        myChart.update()

      },
      showAddList(column){
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
      roundPrecision(){
        this.precision = Math.round(Number(this.precision))
        if(this.precision > 14){
          this.precision = 14
        }
      },
      load(){
        axios.get(this.configsURL + '/' + this.id).then( 
            response => { 
                console.log(response.data)
                this.id = response.data._id
                if(response.data.cohorts){
                  this.cohorts = response.data.cohorts
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
                this.distribution = response.data.distribution
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