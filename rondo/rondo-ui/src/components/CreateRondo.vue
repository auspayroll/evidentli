<template>
  <div>

        <span>- <strong>NEW RONDO</strong> -</span>
        <p/>
        <!--
        <div class="nav">
          <button :class="activePanel == 'cohort' ? 'btn-primary': 'btn-secondary'" @click="activePanel='cohort'">Cohorts</button>
          <button  :class="activePanel == 'pairs' ? 'btn-primary': 'btn-secondary'" @click="activePanel='pairs'">Matched Pairs</button>
        </div>
        -->

        <transition-group name="fade" mode="out-in" class="panel">
          <div key="cohort_panel" class="panel" v-if="activePanel=='cohort'">

            <h4>Name</h4>
            <input name="new_cohort" type="text" placeholder="RONDO name" ref="name" v-model="name"> 
            <p/>
            <div v-show="error" class="alert-danger">{{ error }}</div>
            
            <h4>Cohorts</h4>
            <textarea style="height:90px;font-size:large" v-model="cohortsText" placeholder="enter cohort names, separated by command, eg. A, B, C etc.."></textarea>

            <p/>
            <h4>Matched Pairs</h4>
            <textarea style="height:90px;font-size:large" v-model="matchedPairsText" rows="3" placeholder="enter field names, seperated by commas, eg. age, gender, etc.."></textarea>

          </div>

          
        </transition-group>

        
  <button name="save" type="button" class="btn-success" @click="save">Save</button>
  <code>

  </code>
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
        panel_toggle: true, 
        matchedPairs: '', 
        activePanel: 'cohort',
        cohortsText: '',
        matchedPairsText: ''
      }
    },
    mounted(){
        //this.$refs.name.$el.focus()
        //this.$refs.name.focus();
    },
    computed: {
        configsURL: function(){
            return '/projects/' + this.projectId + '/rondo'
        }
    },
    methods: {
      save(){
            var cohorts = this.cohortsText.split(',')
            cohorts = cohorts.map(s => s.trim());
            var matchedPairs = this.matchedPairsText.split(',')
            matchedPairs = matchedPairs.map(s => s.trim());
            var name = this.name
            var saveObject = { cohorts, matched_pairs: matchedPairs, name }
            console.log(saveObject)
            axios.post(this.configsURL, saveObject).then( response => {
              var _id = response.data._id
              console.log(_id)
              this.$router.push({name: 'rondo', params: { id: _id } })
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

  button {
    margin-right: 1px;
  }

  textarea {
    width: 100%;
    height: 300px;
  }

</style>