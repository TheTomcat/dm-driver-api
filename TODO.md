# Fix Endpoint 
 - [ ] PATCH /images/{image_id}/tag?tag_id=x -> put tag_id into body
 - [ ] DELETE /images/{image_id}/tag?tag_id=x -> put tag_id into body

# Add tests
 - [ ] images /images/{image_id}/full
 - [ ] images /images/{image_id}/thumb
 - [ ] images /images/{image_id}/b64

# Logic
 - [ ] Fix participant.conditions mapping from "a,b,c" to ["a","b","c"]
 - [ ] Make a proper image hash function
 - [ ] Decide the best way to deal with thumbnails