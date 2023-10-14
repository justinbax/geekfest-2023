<template>
    <v-sheet>
        <div>Login</div>
        <v-btn @click="startLogin()">Sign in with O365</v-btn>
    </v-sheet>
</template>

<script setup lang="ts">
    import { MaybeAccount } from '@/services/auth';
    import { auth } from '@/store/auth';
    import { Api } from '@/services/api'
    auth.initialize().then((account) => {console.log(account)})
    function startLogin(): void {
        auth.login()
    }

    Api.get("http://localhost:8080/en/qualifications" ).then((res) => {console.log(res)})
</script>