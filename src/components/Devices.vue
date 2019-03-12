<template>
	<div>
	    <h2>Devices</h2>
	    <router-link to="/devices/register" tag="button" class="btn btn-success" type="button" id="register_btn">Register Device</router-link>
	   <table class="table table-striped table-hover">
	     <thead>
	     <tr><th>Model</th><th></th></th><th>Serial #</th><th>Location</th><th>Active?</th></tr>
	    </thead>
	     <tr v-for="q in 3"><td>Flow Meter AR332</td>
	     <td>
	     	<router-link to="/devices/update">Settings</router-link> | 
	     	<router-link to="/devices/chart">Graph</router-link></a></td></td><td>FM67786</td>
	     <td>Sector 7G</td><td>No</td></tr>

	   </table>
   </div>

</template>


<script>



</script>



<style>



</style>