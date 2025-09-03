function getAdminMetaConfig() {
    const metaTag = document.querySelector('meta[name="admin_config"]');
    if (metaTag) {
      try {
        const content = metaTag.getAttribute("content").replaceAll("'", '"');
        return JSON.parse(content);
      } catch (err) {
        console.error("Error while parsing meta tag config:", err);
      }
    } else {
      console.error('Meta tag with name "admin_config" was not found');
    }
    return {};
}
function getScriptConfig() {
    const configScript = document.getElementById('config-data');
    if (configScript) {
      try {
        return JSON.parse(configScript.textContent);
      } catch (err) {
        console.error("Error while parsing config-data from script:", err);
      }
    } else {
      console.error('Element with id "config-data" was not found');
    }
    return {};
}
function getMergedConfig() {
    const metaConfig = getAdminMetaConfig();
    const scriptConfig = getScriptConfig();
    return { ...metaConfig, ...scriptConfig };
}
window.config = {
  ...(window.config || {}),
  ...getMergedConfig()
};