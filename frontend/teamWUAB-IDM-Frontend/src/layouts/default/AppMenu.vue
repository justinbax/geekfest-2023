<template>
    <v-navigation-drawer>
    <v-list nav>
      <v-list-item v-for="(item,i) in drawerItems" :key = "item.value" :value="item" :prepend-icon="item.icon"
        :to="item.path" color="bg-primary">
        <v-list-item-title v-text="item.title"></v-list-item-title>
      </v-list-item>
     </v-list>
  </v-navigation-drawer>
</template>


<script lang="ts" setup>
    import { ref, Ref } from 'vue';
    type MenuItem = {
        title: string,
        value: number,
        path: string,
        icon?: string
    }
    let drawerItems: Ref<MenuItem[]> = ref([
        {
            title: "Home",
            value: 0,
            path: "/home",
            icon: "mdi-home"
        },
        {
            title: "Apply & Requests",
            value: 2,
            path: "/apply",
        },
        {
            title: "Notifications",
            value: 3,
            path: "/requests",
        },
        {
            title: "Login",
            value: 1,
            path: "/login",
            icon: "mdi-lock"
        },
    ])

</script>
