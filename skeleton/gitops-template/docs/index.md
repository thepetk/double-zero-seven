# Agentic AI Framework Template Gitops

This repository contains the necessary content required for managing GitOps. It was created as part of an Agentic AI Framework Template. The associated source component is available for reference in the **Overview** tab. You can find an example of this reference in the following image.

![Overview Tab](./images/overview-dependency.png)

# Deployed Resources

Based on the input from the Agentic AI Framework Template, a deployment with the following characterisics was made:

# Application

An application built from ${{ values.srcRepoURL }} will be stored in [${{ values.imageRegistry }}/${{ values.imageOrg }}/${{ values.imageName }}](https://${{ values.imageRegistry }}/${{ values.imageOrg }}/${{ values.imageName }}) and deployed through GitOps. This application is accessible on port **${{ values.appPort }}\*\*.
