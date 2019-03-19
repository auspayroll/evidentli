<template>
  <div>

        <span>- <strong>SUMO</strong> {{ id }} -</span>
        <p/>
        <div class="nav">
          <button :class="activePanel == 'summary' ? 'btn-primary': 'btn-secondary'" @click="activePanel='summary'">Cohort Summary</button>
          <button  :class="activePanel == 'comparison' ? 'btn-primary': 'btn-secondary'" @click="activePanel='comparison'">Cohort Comparison</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Summary of matched pairs</button>
        </div>



        <div v-if="errors.length > 0" class="alert-danger">
            <ul v-for="error in errors">
                <li>{{ error }}</li>
            </ul>       
        </div>
        <div v-if="success" class="alert-success">{{ success }}</div>

        <form v-on:submit="save">
        <transition name="fade" mode="out-in" class="panel">
          <div key="cohort_panel" class="panel" v-if="activePanel == 'summary'">

            <div class="form-group row">
                <label for="name" class="col-sm-2 col-form-label">Label of Analysis</label>
                <div class="col-sm-10">
                <input name="name" type="text" placeholder="required" @change="valid" ref="name" v-model="name">
                </div>
            </div>
             <div class="form-group row">
                <label for="cohortDefinition" class="col-sm-2 col-form-label">Cohort Definition</label>
                <div class="col-sm-10">
                <input name="cohortefinition" type="text" placeholder="" v-model="cohortDefinition">
                </div>
            </div>
            <div class="form-group row">
                <label for="fieldAnalysis" class="col-sm-2 col-form-label">Field of Analysis</label>
                <div class="col-sm-10">
                <input name="fieldAnalysis" type="text" placeholder="" v-model="fieldAnalysis">
                </div>
            </div>

            <div class="form-group row">
                <label for="fieldAnalysis" class="col-sm-2 col-form-label">Summaries to include</label>
                <div class="col-sm-10">
                <ul>
                    <li v-for="summary, key in summaries"><input type="checkbox" :value="key" v-model="summarize"> {{ summary }}</li>
                </ul>
                </div>
            </div>
         </div>

          <div key="matched_panel" class="panel" v-if="activePanel == 'comparison'">
                    <div class="form-group row">
                        <label for="name" class="col-sm-2 col-form-label">Label of Analysis</label>
                        <div class="col-sm-10">
                        <input name="name" type="text" placeholder="required" @change="valid" ref="name" v-model="name">
                        </div>
                    </div>
                    <div class="form-group row">
                        <label for="cohortDefinition" class="col-sm-2 col-form-label">Difference between Cohorts</label>
                        <div class="col-sm-10">
                        <input name="cohortefinition" type="text" placeholder="cohort 1"> <input name="cohortefinition" type="text" placeholder="cohort 2" >
                        </div>
                    </div>
                    <div class="form-group row">
                        <label for="fieldAnalysis" class="col-sm-2 col-form-label">Field of Analysis</label>
                        <div class="col-sm-10">
                        <input name="fieldAnalysis" type="text" placeholder="" v-model="fieldAnalysis">
                        </div>
                    </div>

                    <div class="form-group row">
                        <label for="fieldAnalysis" class="col-sm-2 col-form-label">Summaries to include</label>
                        <div class="col-sm-10">
                        <ul>
                            <li v-for="summary, key in comparisonSummaries"><input type="checkbox" :value="key" v-model="summarize"> {{ summary }}</li>
                        </ul>
                        </div>
                    </div>
          </div>

          <div key="matched_panel" class="panel" v-if="activePanel == 'pairs'">
                        <div class="form-group row">
                <label for="name" class="col-sm-2 col-form-label">Label of Analysis</label>
                <div class="col-sm-10">
                <input name="name" type="text" placeholder="required" @change="valid" ref="name" v-model="name">
                </div>
            </div>
             <div class="form-group row">
                <label for="cohortDefinition" class="col-sm-2 col-form-label">Difference between Pairs in</label>
                <div class="col-sm-10">
                <input name="cohortefinition" type="text" placeholder="cohort 1"> <input name="cohortefinition" type="text" placeholder="cohort 2">
                </div>
            </div>
            <div class="form-group row">
                <label for="fieldAnalysis" class="col-sm-2 col-form-label">Field of Analysis</label>
                <div class="col-sm-10">
                <input name="fieldAnalysis" type="text" placeholder="" v-model="fieldAnalysis">
                </div>
            </div>

            <div class="form-group row">
                <label for="fieldAnalysis" class="col-sm-2 col-form-label">Summaries to include</label>
                <div class="col-sm-10">
                <ul>
                    <li v-for="summary, key in summaries"><input type="checkbox" :value="key" v-model="summarize"> {{ summary }}</li>
                </ul>
                </div>
            </div>


          </div>
        </transition>
        <button type="button" class="btn-success" @click="save">Save</button>
        </form>
        

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
        activePanel: 'summary',
        cohorts: [],
        config_name: '', 
        name: '', 
        errors: [],
        success: '',
        panel_toggle: true, 
        summaries: { 'std': 'Standard Deviation', 'mean': 'Mean', 'median': 'Median', 'iqr': 'Inter-quartile range'}, 
        comparisonSummaries: {'mean': 'Difference of means', 'or': 'Odds Ratio', 'median': 'Difference of Medians'},
        matchedSummaries: { 'mean': 'Mean of differences', 'std': 'Standard Deviation of differences', 'median': 'Median of differences', 'iqr': 'IQR of differences'},
        summarize: [],
        cohortDefinition: '',
        fieldAnalysis: '',
        serverData: {},
        summarize_error: ''
      }
    },
    created(){
        axios.get(this.configsURL + '/' + this.id).then( 
            response => { 
                this.serverData = response.data
                this.id  = response.data._id;
                this.cohortDefinition  = response.data.cohortDefinition;
                this.fieldAnalysis = response.data.fieldAnalysis;
                this.summarize = response.data.summarize;
                this.name = response.data.name;
            }
        ).catch(error => {

        })
    },
    mounted(){
        //this.$refs.name.$el.focus()
        this.$refs.name.focus();
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/python-sandbox'
        },
        saveObject: function(){
            return { 
                _id: this.id, 
                summarize: this.summarize,
                cohortDefinition: this.cohortDefinition, 
                name: this.name,
                fieldAnalysis: this.fieldAnalysis,
                type: 'sumo'
            }
        }
    },
    methods: {
    
      save(e){
            e.preventDefault()
            console.log('saving')
            
            if(this.valid()){
                console.log('valid');
                axios.post(this.configsURL, [this.saveObject]).then( response => {
                    console.log(this.saveObject);
                    console.log(response)
                    this.errors = []
                    this.success = 'processor updated'
                }).catch(error => {
                    this.errors.push(error);
                });
            } else {
                
            }
            
      }, 
      valid(){
          this.errors = [];
          this.success = '';
          if(this.name.trim() === ''){
             this.errors.push("Name is required");
              
          }
          if(this.errors.length == 0){
              return true;
          } else {
              return false;
          }
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

  button{
      margin-right:1px;
  }

</style>