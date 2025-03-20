import os
import json
import shutil
import zipfile
from io import BytesIO
import streamlit as st

def create_gatsby_project(extract_json: str):
    """
    1) Copies 'devfolio' -> 'temp/devfolio'
    2) Parses the 'extract_json' for siteMetadata, overwrites 'gatsby-config.js' in 'temp/devfolio'
    3) Zips up 'temp/devfolio' in memory
    4) Returns a Streamlit download button
    """

    # 1) Copy devfolio folder into temp/devfolio (no overwrite of original)
    src_folder = "devfolio"           # Where your original devfolio is
    temp_folder = os.path.join("temp", "devfolio")  # The new location

    # Make sure 'temp' exists
    os.makedirs("temp", exist_ok=True)
    
    # Copy the folder, allowing overwrites if 'temp/devfolio' already exists
    shutil.copytree(src_folder, temp_folder, dirs_exist_ok=True)

    # 2) Parse the JSON data, build a new gatsby-config.js content
    data = json.loads(extract_json)

    new_gatsby_config = f"""module.exports = {{
  siteMetadata: {{
    siteUrl: `{data.get("siteUrl", "https://maze.toys/mazes/mini/daily/")}`,
    name: '{data.get("name", "John Doe")}',
    title: `{data.get("title", "John Doe | Software Engineer")}`,
    description: `{data.get("description", "")}`,
    author: `{data.get("author", "")}`,
    github: `{data.get("github", "")}`,
    linkedin: `{data.get("linkedin", "")}`,
    about: `{data.get("about", "")}`,
    projects: {json.dumps(data.get("projects", []), indent=2)},
    experience: {json.dumps(data.get("experience", []), indent=2)},
    skills: {json.dumps(data.get("skills", []), indent=2)},
  }},
  plugins: [
    `gatsby-plugin-react-helmet`,
    `gatsby-plugin-image`,
    {{
      resolve: `gatsby-source-filesystem`,
      options: {{
        name: `images`,
        path: `${{__dirname}}/src/images`,
      }},
    }},
    {{
      resolve: `gatsby-source-filesystem`,
      options: {{
        path: `${{__dirname}}/content/blog`,
        name: `blog`,
      }},
    }},
    {{
      resolve: `gatsby-transformer-remark`,
      options: {{
        plugins: [
          {{
            resolve: `gatsby-remark-images`,
            options: {{
              maxWidth: 590,
              wrapperStyle: `margin: 0 0 30px;`,
            }},
          }},
          {{
            resolve: `gatsby-remark-responsive-iframe`,
            options: {{
              wrapperStyle: `margin-bottom: 1.0725rem`,
            }},
          }},
          `gatsby-remark-prismjs`,
          `gatsby-remark-copy-linked-files`,
          `gatsby-remark-smartypants`,
        ],
      }},
    }},
    {{
      resolve: `gatsby-plugin-sharp`,
      options: {{
        defaults: {{
          formats: [`auto`, `webp`],
          placeholder: `dominantColor`,
          quality: 80,
        }},
      }},
    }},
    `gatsby-transformer-sharp`,
    `gatsby-plugin-postcss`,
    {{
      resolve: `gatsby-plugin-feed`,
      options: {{
        query: `
          {{
            site {{
              siteMetadata {{
                title
                description
                siteUrl
                site_url: siteUrl
              }}
            }}
          }}
        `,
        feeds: [
          {{
            serialize: ({{ query: {{ site, allMarkdownRemark }} }}) => {{
              return allMarkdownRemark.edges.map((edge) => {{
                return Object.assign({{}}, edge.node.frontmatter, {{
                  description: edge.node.excerpt,
                  date: edge.node.frontmatter.date,
                  url: site.siteMetadata.siteUrl + edge.node.fields.slug,
                  guid: site.siteMetadata.siteUrl + edge.node.fields.slug,
                  custom_elements: [{{ 'content:encoded': edge.node.html }}],
                }});
              }});
            }},
            query: `
              {{
                allMarkdownRemark(
                  sort: {{ frontmatter: {{ date: DESC }} }}
                ) {{
                  edges {{
                    node {{
                      excerpt
                      html
                      fields {{ slug }}
                      frontmatter {{
                        title
                        date
                      }}
                    }}
                  }}
                }}
              }}
            `,
            output: '/rss.xml',
            title: "Your Site's RSS Feed",
          }},
        ],
      }},
    }},
    {{
      resolve: `gatsby-plugin-google-analytics`,
      options: {{
        trackingId: `ADD YOUR TRACKING ID HERE`,
      }},
    }},
    {{
      resolve: `gatsby-plugin-manifest`,
      options: {{
        name: `devfolio`,
        short_name: `devfolio`,
        start_url: `/`,
        background_color: `#663399`,
        theme_color: `#663399`,
        display: `minimal-ui`,
        icon: `src/images/icon.png`,
      }},
    }},
  ],
}};
"""

    config_path = os.path.join(temp_folder, "gatsby-config.js")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_gatsby_config)

    st.success(f"Breathe in, Breathe out, Your Zip File will be ready in a bit")

    # 3) Zip the temp/devfolio folder
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                full_path = os.path.join(root, file)
                # Put files in the archive relative to 'temp/devfolio'
                arcname = os.path.relpath(full_path, start="temp")
                zf.write(full_path, arcname=arcname)
    zip_buffer.seek(0)

    # 4) Provide a Streamlit download button for the zipped result
    st.download_button(
        label="Download Updated Devfolio (Zip)",
        data=zip_buffer,
        file_name="devfolio_updated.zip",
        mime="application/octet-stream"
    )