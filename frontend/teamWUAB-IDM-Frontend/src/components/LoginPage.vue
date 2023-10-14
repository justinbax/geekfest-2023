<template>
    <v-sheet>
        <div>Login</div>
        <v-btn v-if="!auth.account" @click="startLogin()">Sign in with O365</v-btn>
        <v-btn v-else @click="auth.logout()">Sign Out</v-btn>
    </v-sheet>
</template>

<script setup lang="ts">
    import { MaybeAccount } from '@/services/auth';
    import { auth } from '@/store/auth';
    auth.initialize().then((account) => {console.log(account)})
    function startLogin(): void {
        auth.login()
    }

</script>